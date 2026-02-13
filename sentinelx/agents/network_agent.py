"""
Network Analysis Agent — LangGraph Node
Analyzes destination_ip. Static threat intel + Gemini reasoning.
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

KNOWN_MALICIOUS_IPS = {
    "45.77.12.90",
    "185.220.101.1",
    "91.219.237.229",
    "104.248.18.100",
    "23.129.64.130",
}

SYSTEM_PROMPT = """You are a network security analyst in a SOC.
Analyze the given destination IP address for suspicious indicators.

Consider:
- Known bad ranges, bulletproof hosting, Tor exit nodes
- Geo-location anomalies
- C2 beaconing patterns

Respond ONLY with valid JSON:
{
    "network_suspicious": true/false,
    "reason": "short explanation"
}"""


def network_node(state: SentinelState) -> dict:
    """Analyze destination_ip for suspicious network activity."""
    skip = {"network_output": {"network_suspicious": False, "reason": "Not invoked"}}

    if not state.get("invoke_network"):
        return skip

    dest_ip = state["log_data"].get("destination_ip", "")
    if not dest_ip:
        return {"network_output": {"network_suspicious": False, "reason": "No destination IP"}}

    # Quick static check
    if dest_ip in KNOWN_MALICIOUS_IPS:
        return {
            "network_output": {
                "network_suspicious": True,
                "reason": f"IP {dest_ip} is in static threat intelligence list",
            }
        }

    # Gemini analysis
    prompt = f"""{SYSTEM_PROMPT}

Destination IP: {dest_ip}
Source Host: {state['log_data'].get('host', 'unknown')}"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"network_suspicious": False, "reason": "Analysis inconclusive"}

    return {"network_output": result}
