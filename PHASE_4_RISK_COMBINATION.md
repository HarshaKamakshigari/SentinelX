SentinelX v4 – Phase 4 Implementation
Risk Combination & Non-Linear Scaling Layer

Version: SentinelX v4 – Phase 4

Goal:

Combine heuristic risk and graph anomaly signals into a single normalized risk score and apply non-linear amplification to prioritize dangerous events.

This risk signal becomes the core decision variable for the RAMOA orchestrator.

1. Why This Layer Exists

After Phase 3, SentinelX produces two signals:

HeuristicRisk
GraphAnomalyScore

These signals represent different types of intelligence:

Signal	Meaning
HeuristicRisk	rule-based suspicious indicators
GraphAnomalyScore	behavioral anomaly

They must be combined into one final risk signal.

2. SentinelX Pipeline After Phase 4

Before:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
graph_layer
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
risk_combiner
 ↓
orchestrator
3. New Module Structure

Create directory if not existing:

sentinelx/
 ├ risk/
 │   risk_combiner.py
4. Risk Combination Concept

We compute:

EstimatedRisk =
  w1 × HeuristicRisk
+ w2 × GraphAnomalyScore

Recommended weights:

w1 = 0.6
w2 = 0.4

This prioritizes known malicious signals but still considers behavioral anomalies.

5. Non-Linear Risk Scaling

To emphasize dangerous events we apply:

ScaledRisk = (EstimatedRisk)^k

Where:

k = 2

Effect:

EstimatedRisk	ScaledRisk
0.1	0.01
0.3	0.09
0.7	0.49
0.9	0.81

This:

• suppresses low-risk noise
• amplifies high-risk threats

6. Configuration

Modify:

sentinelx/config.py

Add:

RISK_COMBINATION_WEIGHTS = {
    "heuristic": 0.6,
    "graph": 0.4
}

RISK_SCALING_POWER = 2
7. Risk Combiner Module

Create:

sentinelx/risk/risk_combiner.py

Implementation:

from ..models.state import SentinelState
from ..config import RISK_COMBINATION_WEIGHTS, RISK_SCALING_POWER


def combine_risk(heuristic, graph):

    w_h = RISK_COMBINATION_WEIGHTS["heuristic"]
    w_g = RISK_COMBINATION_WEIGHTS["graph"]

    estimated = (w_h * heuristic) + (w_g * graph)

    scaled = estimated ** RISK_SCALING_POWER

    return estimated, scaled


def risk_combiner_node(state: SentinelState):

    heuristic = state.get("heuristic_risk", 0)
    graph = state.get("graph_anomaly_score", 0)

    estimated, scaled = combine_risk(heuristic, graph)

    return {
        "estimated_risk": estimated,
        "scaled_risk": scaled
    }
8. Update SentinelState

Modify:

sentinelx/models/state.py

Add fields:

estimated_risk: float
scaled_risk: float

Example:

heuristic_risk: float
graph_anomaly_score: float
estimated_risk: float
scaled_risk: float
9. Router Integration

Modify:

sentinelx/core/router.py

Import:

from ..risk.risk_combiner import risk_combiner_node

Add node:

graph.add_node("risk_combiner", risk_combiner_node)
10. Update Pipeline

Current pipeline:

normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
orchestrator

Change to:

normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
risk_combiner
 ↓
orchestrator

Implementation:

graph.add_edge("graph_layer", "risk_combiner")

graph.add_edge("risk_combiner", "orchestrator")
11. Orchestrator Preparation

Update orchestrator_node to access:

state["scaled_risk"]

Example logic:

risk = state.get("scaled_risk", 0)

if risk < 0.1:
    skip_all_agents = True

Low-risk events can be ignored or minimally analyzed.

12. Logging

Add logging inside risk_combiner_node.

logger.info(
 "Risk combination: heuristic=%.2f graph=%.2f estimated=%.2f scaled=%.2f",
 heuristic,
 graph,
 estimated,
 scaled
)
13. Example

Input event:

powershell.exe → rare IP

Signals:

heuristic_risk = 0.5
graph_anomaly = 0.7

Estimated risk:

0.6 × 0.5 + 0.4 × 0.7
= 0.58

Scaled risk:

0.58² = 0.34

This score drives agent invocation decisions.

14. Testing

Test using:

POST /ingest

Example:

{
 "host":"finance-01",
 "event_type":"process_creation",
 "command_line":"powershell.exe -enc ABC123",
 "destination_ip":"45.77.12.90"
}

Expected logs:

heuristic_risk = 0.45
graph_anomaly = 0.60
estimated_risk = 0.51
scaled_risk = 0.26
15. Deliverables

After Phase 4 repository contains:

sentinelx/
 ├ risk/
 │   heuristic_risk.py
 │   risk_combiner.py

Updated:

router.py
state.py
config.py
16. SentinelX After Phase 4

Pipeline becomes:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
graph_layer
 ↓
risk_combiner
 ↓
orchestrator
 ↓
agents
 ↓
triage
 ↓
report

SentinelX now has a mathematically grounded risk signal.