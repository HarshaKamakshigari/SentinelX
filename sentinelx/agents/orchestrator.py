"""
Orchestrator Agent — LangGraph Node
Uses Gemini to classify event type and decide which agents to invoke.
Now includes threat intelligence plus pre-orchestration scoring awareness.
"""
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from ..models.state import SentinelState

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

SYSTEM_PROMPT = """You are a Security Operations Center orchestrator.
Given a security log event, decide which specialist agents should analyze it.

Rules:
- The heuristic_risk and graph_anomaly_score fields are upstream anomaly signals.
- If both scores are very low (< 0.20) and the log has no strong artifact (hash, IP, suspicious command), prefer skipping expensive agents.
- If command_line contains suspicious patterns (powershell, encoded commands, 
  rundll32, mshta, wget, curl to suspicious URLs, or any LOLBin abuse) → invoke_malware = true
- If destination_ip is present → invoke_network = true
- If file_hash is present → invoke_vt = true
- If file_hash is present → invoke_threatintel = true

Respond ONLY with valid JSON, no extra text:
{
    "invoke_malware": true/false,
    "invoke_network": true/false,
    "invoke_vt": true/false,
    "invoke_threatintel": true/false
}"""


def orchestrator_node(state: SentinelState) -> dict:
    """Classify event and decide routing."""
    log_data = state.get("normalized_event") or state["log_data"]
    heuristic_risk = state.get("heuristic_risk", 0.0)
    graph_anomaly_score = state.get("graph_anomaly_score", 0.0)
    scaled_risk = state.get("scaled_risk", 0.0)
    command_line = (log_data.get("command_line") or "").lower()
    has_hash = bool(log_data.get("file_hash"))
    has_ip = bool(log_data.get("destination_ip"))
    suspicious_command = any(
        token in command_line for token in ["powershell", "-enc", "rundll32", "mshta", "certutil", "bitsadmin"]
    )

    if scaled_risk < 0.1 and not any([has_hash, has_ip, suspicious_command]):
        return {
            "invoke_malware": False,
            "invoke_network": False,
            "invoke_vt": False,
            "invoke_threatintel": False,
        }

    prompt = f"""{SYSTEM_PROMPT}

Upstream Scores:
{json.dumps({
    "heuristic_risk": heuristic_risk,
    "graph_anomaly_score": graph_anomaly_score,
}, indent=2)}

Security Log:
{json.dumps(log_data, indent=2)}"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    # Strip markdown fences if present
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        decision = json.loads(content)
    except json.JSONDecodeError:
        decision = {
            "invoke_malware": suspicious_command or heuristic_risk >= 0.35 or graph_anomaly_score >= 0.4,
            "invoke_network": has_ip or graph_anomaly_score >= 0.35,
            "invoke_vt": has_hash,
            "invoke_threatintel": has_hash,
        }

    return {
        "invoke_malware": decision.get("invoke_malware", False),
        "invoke_network": decision.get("invoke_network", False),
        "invoke_vt": decision.get("invoke_vt", False),
        "invoke_threatintel": decision.get("invoke_threatintel", bool(log_data.get("file_hash"))),
    }
