"""
Report Agent — LangGraph Node
Generates structured SOC-style incident report using Gemini.
Includes threat intelligence enrichment in the final report.
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
- Reference threat intelligence findings where available

Respond ONLY with valid JSON:
{
    "summary": "Detailed incident summary",
    "mitre_techniques": ["T1059.001"],
    "timeline": [
        "Event detected on host X",
        "Malware agent flagged encoded PowerShell",
        "Threat intelligence identified XWorm malware family"
    ]
}"""


def report_node(state: SentinelState) -> dict:
    """Generate final incident report using Gemini with threat intel enrichment."""
    findings = {
        "log": state.get("log_data", {}),
        "severity": state.get("severity", "MEDIUM"),
        "confidence": state.get("confidence", 0.5),
        "triage_reason": state.get("triage_reason", ""),
        "malware": state.get("malware_output", {}),
        "network": state.get("network_output", {}),
        "virustotal": state.get("vt_output", {}),
        "threat_intelligence": state.get("threatintel_output", {}),
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
    if state.get("invoke_threatintel"):
        agents_invoked.append("ThreatIntelAgent")
    if state.get("invoke_vt"):
        agents_invoked.append("VirusTotalAgent")

    # Build threat intelligence section for the report
    threatintel_output = state.get("threatintel_output", {})
    threat_intel_section = None
    if threatintel_output.get("threat_match"):
        threat_intel_section = {
            "malware_family": threatintel_output.get("malware_family", "Unknown"),
            "file_name": threatintel_output.get("file_name", ""),
            "file_type": threatintel_output.get("file_type", ""),
            "vt_percent": threatintel_output.get("vt_percent"),
            "source": threatintel_output.get("source", "MalwareBazaar"),
        }

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
            "threat_intelligence": threatintel_output,
        },
        "threat_intelligence": threat_intel_section,
    }

    return {"final_report": final_report}
