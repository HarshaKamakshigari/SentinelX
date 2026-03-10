"""Temporal behavioral graph primitives."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping

import networkx as nx

temporal_graph = nx.DiGraph()
EDGE_TTL_SECONDS = 3600

_GRAPH_LOCK = RLock()


def _utc_timestamp() -> float:
    return datetime.now(timezone.utc).timestamp()


def _string_value(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _node_id(node_type: str, value: Any) -> str | None:
    normalized = _string_value(value)
    if not normalized:
        return None
    return f"{node_type}:{normalized}"


def process_node_from_event(event: Mapping[str, Any]) -> str | None:
    return _node_id("process", event.get("process_name"))


def _file_node_from_event(event: Mapping[str, Any]) -> str | None:
    return _node_id("file", event.get("file_name") or event.get("file_hash"))


def _is_file_write_event(event: Mapping[str, Any]) -> bool:
    event_type = _string_value(event.get("event_type"))
    if not event_type:
        return False
    event_type = event_type.lower()
    return event_type in {"file_create", "file_write", "file_modify", "file_modification"}


def event_edges(event: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    """Project a normalized event into graph relationships."""
    edges: list[tuple[str, str, str]] = []

    host_node = _node_id("host", event.get("host"))
    process_node = process_node_from_event(event)
    parent_process_node = _node_id("process", event.get("parent_process"))
    user_node = _node_id("user", event.get("user_id"))
    dest_ip_node = _node_id("ip", event.get("destination_ip"))
    file_node = _file_node_from_event(event)

    if process_node and host_node:
        edges.append((process_node, host_node, "ran_on"))

    if parent_process_node and process_node and parent_process_node != process_node:
        edges.append((parent_process_node, process_node, "spawned"))

    if user_node and process_node:
        edges.append((user_node, process_node, "executed_by"))

    if process_node and dest_ip_node:
        edges.append((process_node, dest_ip_node, "connected_to"))

    if process_node and file_node and _is_file_write_event(event):
        edges.append((process_node, file_node, "wrote_file"))

    return edges


def add_nodes(event: Mapping[str, Any]) -> list[str]:
    """Inject graph nodes for supported event entities."""
    node_specs = [
        ("host", event.get("host")),
        ("user", event.get("user_id")),
        ("process", event.get("process_name")),
        ("process", event.get("parent_process")),
        ("ip", event.get("destination_ip")),
        ("file", event.get("file_name") or event.get("file_hash")),
    ]

    added_nodes: list[str] = []

    with _GRAPH_LOCK:
        for node_type, raw_value in node_specs:
            node_id = _node_id(node_type, raw_value)
            if not node_id:
                continue
            temporal_graph.add_node(
                node_id,
                node_type=node_type,
                value=_string_value(raw_value),
            )
            added_nodes.append(node_id)

    return added_nodes


def add_edges(event: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    """Inject temporal relationships for a normalized event."""
    now = _utc_timestamp()
    relationships = event_edges(event)

    with _GRAPH_LOCK:
        for source, target, relation in relationships:
            temporal_graph.add_edge(
                source,
                target,
                relation=relation,
                timestamp=now,
            )

    return relationships


def prune_graph(now_ts: float | None = None) -> None:
    """Remove expired edges and orphaned nodes outside the time window."""
    cutoff = now_ts if now_ts is not None else _utc_timestamp()

    with _GRAPH_LOCK:
        expired_edges = []
        for source, target, data in list(temporal_graph.edges(data=True)):
            timestamp = float(data.get("timestamp", 0))
            if cutoff - timestamp > EDGE_TTL_SECONDS:
                expired_edges.append((source, target))

        if expired_edges:
            temporal_graph.remove_edges_from(expired_edges)

        orphaned_nodes = [node for node in list(temporal_graph.nodes) if temporal_graph.degree(node) == 0]
        if orphaned_nodes:
            temporal_graph.remove_nodes_from(orphaned_nodes)


def reset_graph() -> None:
    """Clear the global graph. Intended for tests and local resets."""
    with _GRAPH_LOCK:
        temporal_graph.clear()
