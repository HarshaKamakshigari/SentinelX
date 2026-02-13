"""
Triage Agent — LangGraph Node
Combines all agent outputs. Uses Gemini to assess severity & confidence.
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

Severity levels: LOW, MEDIUM, HIGH, CRITICAL
Confidence: float between 0.0 and 1.0

Respond ONLY with valid JSON:
{
    "severity": "HIGH",
    "confidence": 0.92,
    "reason": "short explanation"
}"""


def triage_node(state: SentinelState) -> dict:
    """Assess severity using Gemini + agent findings."""
    findings = {
        "log": state.get("log_data", {}),
        "malware": state.get("malware_output", {}),
        "network": state.get("network_output", {}),
        "virustotal": state.get("vt_output", {}),
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
