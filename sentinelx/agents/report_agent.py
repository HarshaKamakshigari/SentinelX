"""
Report Agent — LangGraph Node
Generates structured SOC-style incident report using Gemini.
"""
import json
import uuid
from datetime import datetime, timezone
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from ..models.state import SentinelState

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

SYSTEM_PROMPT = """You are a SOC report generator.
Create a comprehensive incident report based on the analysis findings.

Include:
- A concise but detailed summary of what happened
- Timeline of events
- MITRE ATT&CK technique IDs that apply

Respond ONLY with valid JSON:
{
    "summary": "Detailed incident summary",
    "mitre_techniques": ["T1059.001"],
    "timeline": [
        "Event detected on host X",
        "Malware agent flagged encoded PowerShell"
    ]
}"""


def report_node(state: SentinelState) -> dict:
    """Generate final incident report using Gemini."""
    findings = {
        "log": state.get("log_data", {}),
        "severity": state.get("severity", "MEDIUM"),
        "confidence": state.get("confidence", 0.5),
        "triage_reason": state.get("triage_reason", ""),
        "malware": state.get("malware_output", {}),
        "network": state.get("network_output", {}),
        "virustotal": state.get("vt_output", {}),
    }

    prompt = f"""{SYSTEM_PROMPT}

Analysis Data:
{json.dumps(findings, indent=2)}"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        report_data = json.loads(content)
    except json.JSONDecodeError:
        report_data = {
            "summary": state.get("triage_reason", "Incident detected"),
            "mitre_techniques": [],
            "timeline": [],
        }

    agents_invoked = []
    if state.get("invoke_malware"):
        agents_invoked.append("MalwareAgent")
    if state.get("invoke_network"):
        agents_invoked.append("NetworkAgent")
    if state.get("invoke_vt"):
        agents_invoked.append("VirusTotalAgent")

    final_report = {
        "incident_id": f"SOC-{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": state.get("log_data", {}).get("host", "unknown"),
        "summary": report_data.get("summary", ""),
        "severity": state.get("severity", "MEDIUM"),
        "confidence": state.get("confidence", 0.5),
        "mitre_techniques": report_data.get("mitre_techniques", []),
        "timeline": report_data.get("timeline", []),
        "agents_invoked": agents_invoked,
        "details": {
            "malware": state.get("malware_output", {}),
            "network": state.get("network_output", {}),
            "virustotal": state.get("vt_output", {}),
        },
    }

    return {"final_report": final_report}
