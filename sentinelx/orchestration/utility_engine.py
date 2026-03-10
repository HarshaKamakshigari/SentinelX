"""
RAMOA Utility Engine — computes expected utility for each analytical agent.

Formula:
    ExpectedUtility(Ai) = (ScaledRisk × TrustScore[Ai]) − ExecutionCost[Ai]

An agent is invoked only when its utility exceeds the configured threshold.
"""
import logging

from ..config import AGENT_PROFILES, UTILITY_THRESHOLD

logger = logging.getLogger(__name__)


def compute_utility(agent_name: str, scaled_risk: float) -> float:
    """Return the expected utility for *agent_name* given the current scaled risk."""
    profile = AGENT_PROFILES.get(agent_name, {})
    trust = profile.get("trust", 0.5)
    cost = profile.get("cost", 0.1)
    return (scaled_risk * trust) - cost


def should_invoke(agent_name: str, scaled_risk: float) -> tuple[bool, float]:
    """Return (invoke_flag, utility_value) for the agent."""
    utility = compute_utility(agent_name, scaled_risk)
    return utility > UTILITY_THRESHOLD, utility
