"""LangGraph node for temporal graph anomaly scoring."""

from __future__ import annotations

import logging

from ..models.state import SentinelState
from .graph_engine import add_edges, add_nodes, prune_graph
from .graph_metrics import compute_graph_score

logger = logging.getLogger(__name__)


def graph_layer_node(state: SentinelState) -> dict:
    """Update the temporal graph and emit a graph anomaly score."""
    event = state.get("normalized_event") or state.get("log_data", {})

    add_nodes(event)
    add_edges(event)
    prune_graph()

    score = compute_graph_score(event)
    logger.info("Graph anomaly score: %.2f", score)

    return {"graph_anomaly_score": score}
