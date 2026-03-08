SentinelX v4 – Phase 3 Implementation
Graph Intelligence Layer (Temporal Behavioral Graph)

Version: SentinelX v4 – Phase 3

Goal:

Introduce a behavioral graph engine that tracks relationships between processes, users, files, hosts, and IP addresses and computes a Graph Anomaly Score.

This enables SentinelX to detect:

• unusual connections
• rare process activity
• lateral movement patterns
• abnormal relationships

This is the main structural detection mechanism in RAMOA.

1. Why This Layer Exists

Heuristic risk only sees single events.

Example:

powershell.exe -enc ABC

But attacks are multi-step.

Example attack chain:

Word → PowerShell → Download Payload → Connect to C2

A graph captures relationships between these steps.

2. SentinelX Pipeline After Phase 3

Before:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
orchestrator

After:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
orchestrator
3. New Module Structure

Create:

sentinelx/
 ├ graph/
 │   __init__.py
 │   graph_engine.py
 │   graph_metrics.py
4. Dependency

Add to requirements.txt:

networkx

Install:

pip install networkx
5. Graph Data Model

The graph represents entities and relationships.

Nodes
Node Type	Example
Host	finance-01
User	alice
Process	powershell.exe
IP	45.77.12.90
File	payload.exe
Edges
Relationship	Meaning
spawned	process started another process
connected_to	process connected to IP
executed_by	user ran process
wrote_file	process created file
6. Temporal Graph

Create a global graph instance.

File:

sentinelx/graph/graph_engine.py

Implementation:

import networkx as nx
from datetime import datetime

temporal_graph = nx.DiGraph()

EDGE_TTL_SECONDS = 3600

The graph is time-windowed.

Edges older than TTL are removed.

7. Node Injection

When an event arrives, inject nodes.

Example:

host = "finance-01"
process = "powershell.exe"
dest_ip = "45.77.12.90"

Graph representation:

host_finance-01
process_powershell.exe
ip_45.77.12.90
Example Code
def add_nodes(event):

    host = event.get("host")
    process = event.get("process_name")
    dest_ip = event.get("destination_ip")

    if host:
        temporal_graph.add_node(f"host:{host}")

    if process:
        temporal_graph.add_node(f"process:{process}")

    if dest_ip:
        temporal_graph.add_node(f"ip:{dest_ip}")
8. Edge Injection

Edges represent relationships.

Example:

process → ip

Implementation:

def add_edges(event):

    process = event.get("process_name")
    dest_ip = event.get("destination_ip")

    now = datetime.utcnow().timestamp()

    if process and dest_ip:

        temporal_graph.add_edge(
            f"process:{process}",
            f"ip:{dest_ip}",
            relation="connected_to",
            timestamp=now
        )
9. Graph Pruning (Temporal Window)

Old edges must be removed.

Add function:

def prune_graph():

    now = datetime.utcnow().timestamp()

    for u, v, data in list(temporal_graph.edges(data=True)):

        ts = data.get("timestamp", 0)

        if now - ts > EDGE_TTL_SECONDS:

            temporal_graph.remove_edge(u, v)

This keeps graph size manageable.

10. Graph Metrics

Create:

sentinelx/graph/graph_metrics.py
Metric 1 – Degree Deviation

Detect unusual connectivity.

Formula:

Deviation = |current_degree − avg_degree| / avg_degree

Implementation:

node_degree_history = {}

def degree_deviation(node):

    degree = temporal_graph.degree(node)

    avg = node_degree_history.get(node, degree)

    deviation = abs(degree - avg) / max(avg, 1)

    node_degree_history[node] = (avg + degree) / 2

    return deviation
Metric 2 – Rarity Score

Rare relationships are suspicious.

Formula:

Rarity = 1 / (edge_frequency + 1)

Implementation:

edge_frequency = {}

def rarity_score(edge):

    freq = edge_frequency.get(edge, 0)

    edge_frequency[edge] = freq + 1

    return 1 / (freq + 1)
11. Graph Anomaly Score

Combine metrics.

Formula:

GraphScore =
0.5 × DegreeDeviation
+
0.5 × RarityScore

Implementation:

def compute_graph_score(event):

    process = event.get("process_name")
    dest_ip = event.get("destination_ip")

    node = f"process:{process}" if process else None

    edge = (process, dest_ip)

    deviation = degree_deviation(node) if node else 0

    rarity = rarity_score(edge) if process and dest_ip else 0

    return (0.5 * deviation) + (0.5 * rarity)
12. Graph Layer Node

Add LangGraph node.

File:

sentinelx/graph/graph_layer_node.py

Implementation:

from ..models.state import SentinelState
from .graph_engine import add_nodes, add_edges, prune_graph
from .graph_metrics import compute_graph_score


def graph_layer_node(state: SentinelState):

    event = state.get("log_data", {})

    add_nodes(event)

    add_edges(event)

    prune_graph()

    score = compute_graph_score(event)

    return {
        "graph_anomaly_score": score
    }
13. Update SentinelState

Modify:

sentinelx/models/state.py

Add:

graph_anomaly_score: float
14. Update Router

Modify:

sentinelx/core/router.py

Import:

from ..graph.graph_layer_node import graph_layer_node

Add node:

graph.add_node("graph_layer", graph_layer_node)
15. Update Pipeline

Current pipeline:

normalizer
 ↓
heuristic_risk
 ↓
orchestrator

New pipeline:

normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
orchestrator

Implementation:

graph.add_edge("heuristic_risk", "graph_layer")

graph.add_edge("graph_layer", "orchestrator")
16. Example Detection

Example event:

powershell.exe → 45.77.12.90

If connection is rare:

rarity ≈ 0.9
degree deviation ≈ 0.5

Graph score:

GraphScore ≈ 0.7
17. Logging

Add logs:

logger.info(
 "Graph anomaly score: %.2f",
 score
)
18. Testing

Send repeated events.

First connection:

rarity high
score high

Repeated connections:

rarity decreases
score decreases

This mimics behavioral baselining.

19. Deliverables

After Phase 3 repository contains:

sentinelx/
 ├ graph/
 │   graph_engine.py
 │   graph_metrics.py
 │   graph_layer_node.py
 │   __init__.py

Updated:

router.py
state.py
requirements.txt
20. System After Phase 3

SentinelX becomes:

Context-Aware Agentic SOC

Pipeline:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
orchestrator
 ↓
agents
 ↓
triage
 ↓
report

Now the system understands behavioral context.