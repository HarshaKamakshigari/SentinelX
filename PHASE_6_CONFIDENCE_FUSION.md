SentinelX v4 – Phase 6 Implementation
Confidence Fusion Engine

Version: SentinelX v4 – Phase 6

Goal:

Combine outputs from all invoked agents into a single final confidence score and verdict using trust-weighted aggregation.

This allows SentinelX to:

• merge multiple analytical perspectives
• avoid single-agent bias
• produce explainable decisions

1. Why This Layer Exists

After Phase 5 the orchestrator selects agents based on utility:

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
ramoa_orchestrator
 ↓
agents

Each agent returns its own output.

Example:

MalwareAgent → confidence = 0.8
NetworkAgent → confidence = 0.6
ThreatIntelAgent → confidence = 0.9

Without fusion there is no principled way to combine them.

RAMOA introduces trust-weighted confidence fusion.

2. Confidence Fusion Formula

RAMOA defines:

FinalConfidence =
Σ(confidence_i × trust_i)
-------------------------
Σ(trust_i)

Where:

Variable	Meaning
confidence_i	confidence returned by agent
trust_i	trust score of agent
3. Example

Agents produce:

Agent	Confidence	Trust
MalwareAgent	0.8	0.8
NetworkAgent	0.6	0.7
ThreatIntelAgent	0.9	0.9

Fusion:

(0.8×0.8 + 0.6×0.7 + 0.9×0.9)
--------------------------------
(0.8 + 0.7 + 0.9)

Result:

FinalConfidence ≈ 0.78
4. SentinelX Pipeline After Phase 6

Before:

agents
 ↓
triage
 ↓
report

After:

agents
 ↓
fusion
 ↓
triage
 ↓
report

Fusion creates a unified signal for triage.

5. New Module

Create new directory:

sentinelx/
 ├ fusion/
 │   __init__.py
 │   confidence_fusion.py
6. Confidence Fusion Engine

Create file:

sentinelx/fusion/confidence_fusion.py

Implementation:

from ..config import AGENT_PROFILES
from ..models.state import SentinelState


def extract_agent_confidences(state):

    agents = {}

    malware = state.get("malware_output", {})
    network = state.get("network_output", {})
    vt = state.get("vt_output", {})
    threatintel = state.get("threatintel_output", {})

    if malware:
        agents["malware_agent"] = malware.get("confidence", 0)

    if network:
        agents["network_agent"] = network.get("confidence", 0)

    if vt:
        agents["vt_agent"] = vt.get("confidence", 0)

    if threatintel:
        agents["threatintel_agent"] = threatintel.get("confidence", 0)

    return agents
7. Fusion Calculation

Add fusion function.

def fuse_confidence(agent_confidences):

    weighted_sum = 0
    trust_sum = 0

    for agent, confidence in agent_confidences.items():

        trust = AGENT_PROFILES.get(agent, {}).get("trust", 0.5)

        weighted_sum += confidence * trust
        trust_sum += trust

    if trust_sum == 0:
        return 0

    return weighted_sum / trust_sum
8. Fusion Node

Add LangGraph node.

def fusion_node(state: SentinelState):

    agent_confidences = extract_agent_confidences(state)

    final_confidence = fuse_confidence(agent_confidences)

    verdict = "malicious" if final_confidence > 0.7 else "benign"

    return {
        "final_confidence": final_confidence,
        "final_verdict": verdict
    }
9. Update SentinelState

Modify:

sentinelx/models/state.py

Add:

final_confidence: float
final_verdict: str

Example:

scaled_risk: float
agent_utilities: dict
final_confidence: float
final_verdict: str
10. Update Router

Modify:

sentinelx/core/router.py

Import fusion node:

from ..fusion.confidence_fusion import fusion_node

Add node:

graph.add_node("fusion", fusion_node)
11. Update Pipeline

Current:

agents
 ↓
triage
 ↓
report

New:

agents
 ↓
fusion
 ↓
triage
 ↓
report

Implementation:

graph.add_edge("vt_agent", "fusion")
graph.add_edge("fusion", "triage_agent")
12. Update Agents (Small Change)

Agents should return confidence values.

Example MalwareAgent output:

{
 "verdict": "malicious",
 "confidence": 0.85,
 "patterns": [...]
}

ThreatIntelAgent example:

confidence = vt_percent / 100

NetworkAgent example:

confidence = 0.7 if suspicious else 0.1
13. Logging

Add fusion logging.

logger.info(
 "Fusion confidence: %.2f verdict=%s",
 final_confidence,
 verdict
)
14. Example Event

Event:

powershell.exe -enc ABC → connects to rare IP

Agent results:

MalwareAgent confidence = 0.8
NetworkAgent confidence = 0.7
ThreatIntelAgent confidence = 0.9

Fusion result:

FinalConfidence = 0.82
Verdict = malicious
15. Deliverables

After Phase 6 repository contains:

sentinelx/
 ├ fusion/
 │   confidence_fusion.py
 │   __init__.py

Updated files:

router.py
state.py
agents/*
16. SentinelX After Phase 6

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
ramoa_orchestrator
 ↓
agents
 ↓
fusion
 ↓
triage
 ↓
report
What Phase 6 Achieves

SentinelX now supports:

• multi-agent consensus
• trust-weighted decisions
• explainable SOC verdicts

This is core RAMOA behavior.