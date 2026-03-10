"""
Triage Agent — LangGraph Node
Combines all agent outputs including threat intelligence.
Uses Gemini to assess severity & confidence.
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

SYSTEM_PROMPT = """You are a senior SOC triage analyst.
Given the original security log and findings from specialist agents,
assign an overall severity and confidence score.

Consider all available intelligence:
- Heuristic risk and graph anomaly signals from the pre-orchestration pipeline
- Malware analysis patterns and MITRE techniques
- Network analysis findings
- VirusTotal detection results
- Threat Intelligence KB matches (known malware families, detection rates)

If the threat intelligence matched a known malware family:
  - This significantly increases confidence
  - Known families like XWorm, Mirai, RemcosRAT etc. warrant HIGH or CRITICAL severity
  - High VT detection percentage (>50%) supports elevation to CRITICAL

File type risk considerations:
  - exe, dll, elf → higher risk
  - documents with macros → medium-high risk
  - scripts (js, vbs, ps1, bat) → medium risk

Severity levels: LOW, MEDIUM, HIGH, CRITICAL
Confidence: float between 0.0 and 1.0

Respond ONLY with valid JSON:
{
    "severity": "HIGH",
    "confidence": 0.92,
    "reason": "short explanation"
}"""


def triage_node(state: SentinelState) -> dict:
    """Assess severity using Gemini + agent findings including threat intel."""
    findings = {
        "log": state.get("log_data", {}),
        "heuristic_risk": state.get("heuristic_risk", 0.0),
        "graph_anomaly_score": state.get("graph_anomaly_score", 0.0),
        "malware": state.get("malware_output", {}),
        "network": state.get("network_output", {}),
        "virustotal": state.get("vt_output", {}),
        "threat_intelligence": state.get("threatintel_output", {}),
    }

    prompt = f"""{SYSTEM_PROMPT}

Agent Findings:
{json.dumps(findings, indent=2)}"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"severity": "MEDIUM", "confidence": 0.5, "reason": "Triage parse error"}

    return {
        "severity": result.get("severity", "MEDIUM"),
        "confidence": result.get("confidence", 0.5),
        "triage_reason": result.get("reason", ""),
    }
