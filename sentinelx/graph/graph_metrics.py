"""Graph anomaly metrics for the temporal behavioral graph."""

from __future__ import annotations

from threading import RLock
from typing import Any, Mapping

from .graph_engine import event_edges, process_node_from_event, temporal_graph

node_degree_history: dict[str, dict[str, float]] = {}
edge_frequency: dict[tuple[str, str, str], int] = {}

_METRIC_LOCK = RLock()


def degree_deviation(node: str | None) -> float:
    """Measure deviation from the node's running degree baseline."""
    if not node or node not in temporal_graph:
        return 0.0

    degree = float(temporal_graph.degree(node))

    with _METRIC_LOCK:
        record = node_degree_history.get(node)
        if not record:
            node_degree_history[node] = {"total": degree, "count": 1.0}
            return 0.0

        average = record["total"] / max(record["count"], 1.0)
        deviation = abs(degree - average) / max(average, 1.0)

        record["total"] += degree
        record["count"] += 1.0

    return deviation


def rarity_score(edge: tuple[str, str, str] | None) -> float:
    """Score how uncommon an observed relationship is."""
    if not edge:
        return 0.0

    with _METRIC_LOCK:
        frequency = edge_frequency.get(edge, 0)
        edge_frequency[edge] = frequency + 1

    return 1.0 / (frequency + 1)


def compute_graph_score(event: Mapping[str, Any]) -> float:
    """Combine connectivity deviation and relationship rarity."""
    process_node = process_node_from_event(event)
    deviation = degree_deviation(process_node)

    relationship_edges = event_edges(event)
    if relationship_edges:
        rarity = sum(rarity_score(edge) for edge in relationship_edges) / len(relationship_edges)
    else:
        rarity = 0.0

    return (0.5 * deviation) + (0.5 * rarity)


def reset_graph_metrics() -> None:
    """Clear metric baselines. Intended for tests and local resets."""
    with _METRIC_LOCK:
        node_degree_history.clear()
        edge_frequency.clear()
