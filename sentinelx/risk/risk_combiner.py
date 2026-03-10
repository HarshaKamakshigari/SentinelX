"""
Risk Combiner — combines heuristic risk and graph anomaly into a single
normalized score, then applies non-linear scaling to amplify high-risk events.
"""
import logging

from ..models.state import SentinelState
from ..config import RISK_COMBINATION_WEIGHTS, RISK_SCALING_POWER

logger = logging.getLogger(__name__)


def combine_risk(heuristic: float, graph: float) -> tuple[float, float]:
    """Return (estimated_risk, scaled_risk)."""
    w_h = RISK_COMBINATION_WEIGHTS["heuristic"]
    w_g = RISK_COMBINATION_WEIGHTS["graph"]

    estimated = min(1.0, (w_h * heuristic) + (w_g * graph))
    scaled = estimated ** RISK_SCALING_POWER

    return estimated, scaled


def risk_combiner_node(state: SentinelState) -> dict:
    """LangGraph node — emit combined & scaled risk."""
    heuristic = state.get("heuristic_risk", 0)
    graph = state.get("graph_anomaly_score", 0)

    estimated, scaled = combine_risk(heuristic, graph)

    logger.info(
        "Risk combination: heuristic=%.2f graph=%.2f estimated=%.2f scaled=%.2f",
        heuristic,
        graph,
        estimated,
        scaled,
    )

    return {
        "estimated_risk": estimated,
        "scaled_risk": scaled,
    }
