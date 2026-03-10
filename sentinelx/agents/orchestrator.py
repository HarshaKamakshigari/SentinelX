"""
RAMOA Orchestrator — LangGraph Node

Pure mathematical utility-based agent selection.
No LLM calls. Uses the RAMOA expected utility formula:

    ExpectedUtility(Ai) = (ScaledRisk × TrustScore[Ai]) − ExecutionCost[Ai]

Agents are invoked only when their utility exceeds the configured threshold.
"""
import logging

from ..models.state import SentinelState
from ..orchestration.utility_engine import should_invoke

logger = logging.getLogger(__name__)


def orchestrator_node(state: SentinelState) -> dict:
    """Compute expected utility per agent and set invocation flags."""
    scaled_risk = state.get("scaled_risk", 0.0)

    invoke_malware, malware_util = should_invoke("malware_agent", scaled_risk)
    invoke_network, network_util = should_invoke("network_agent", scaled_risk)
    invoke_threatintel, ti_util = should_invoke("threatintel_agent", scaled_risk)
    invoke_vt, vt_util = should_invoke("vt_agent", scaled_risk)

    agent_utilities = {
        "malware": malware_util,
        "network": network_util,
        "threatintel": ti_util,
        "vt": vt_util,
    }

    logger.info(
        "RAMOA utilities (scaled_risk=%.3f): malware=%.3f network=%.3f threatintel=%.3f vt=%.3f",
        scaled_risk,
        malware_util,
        network_util,
        ti_util,
        vt_util,
    )

    return {
        "invoke_malware": invoke_malware,
        "invoke_network": invoke_network,
        "invoke_vt": invoke_vt,
        "invoke_threatintel": invoke_threatintel,
        "agent_utilities": agent_utilities,
    }
