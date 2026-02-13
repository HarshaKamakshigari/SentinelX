"""
Orchestrator Agent — LangGraph Node
Uses Gemini to classify event type and decide which agents to invoke.
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
- If command_line contains suspicious patterns (powershell, encoded commands, 
  rundll32, mshta, wget, curl to suspicious URLs, or any LOLBin abuse) → invoke_malware = true
- If destination_ip is present → invoke_network = true
- If file_hash is present → invoke_vt = true

Respond ONLY with valid JSON, no extra text:
{
    "invoke_malware": true/false,
    "invoke_network": true/false,
    "invoke_vt": true/false
}"""


def orchestrator_node(state: SentinelState) -> dict:
    """Classify event and decide routing."""
    log_data = state["log_data"]

    prompt = f"""{SYSTEM_PROMPT}

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
        cmd = (log_data.get("command_line") or "").lower()
        decision = {
            "invoke_malware": any(k in cmd for k in ["powershell", "-enc", "rundll32", "mshta"]),
            "invoke_network": bool(log_data.get("destination_ip")),
            "invoke_vt": bool(log_data.get("file_hash")),
        }

    return {
        "invoke_malware": decision.get("invoke_malware", False),
        "invoke_network": decision.get("invoke_network", False),
        "invoke_vt": decision.get("invoke_vt", False),
    }
