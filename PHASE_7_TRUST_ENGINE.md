SentinelX v4 – Phase 7 Implementation
Trust Learning Engine

File name:

PHASE_7_TRUST_ENGINE.md

Goal:

Allow SentinelX to learn which agents are reliable over time and automatically adjust their influence in decision making.

This makes SentinelX self-optimizing.

1. Why Trust Learning Exists

Currently agents have static trust:

AGENT_PROFILES = {
 "malware_agent": {"trust":0.8},
 "network_agent": {"trust":0.7},
 "threatintel_agent":{"trust":0.9},
 "vt_agent":{"trust":0.85}
}

But in reality:

• some agents produce false positives
• some agents are highly accurate
• some degrade over time

RAMOA introduces adaptive trust scoring.

2. Trust Model

Each agent maintains two parameters:

α = successful detections
β = failed detections

Trust score:

Trust = α / (α + β)

Example:

Agent	α	β	Trust
MalwareAgent	8	2	0.8
NetworkAgent	5	5	0.5
3. Trust Store

Create module:

sentinelx/trust/trust_engine.py
4. Trust Store Structure
trust_store = {
 "malware_agent": {"alpha":1,"beta":1},
 "network_agent": {"alpha":1,"beta":1},
 "threatintel_agent":{"alpha":1,"beta":1},
 "vt_agent":{"alpha":1,"beta":1}
}

We initialize with 1,1 to avoid division by zero.

5. Trust Calculation

Add function:

def compute_trust(agent):

    record = trust_store.get(agent)

    alpha = record["alpha"]
    beta = record["beta"]

    return alpha / (alpha + beta)
6. Trust Update Logic

When a final decision is made we update trust.

Rules:

Condition	Update
Agent agrees with final verdict	α += 1
Agent disagrees	β += 1
7. Update Function

Add:

def update_trust(agent, correct):

    record = trust_store.get(agent)

    if correct:
        record["alpha"] += 1
    else:
        record["beta"] += 1
8. Trust Decay

Agents should lose trust slowly if unused.

Add decay:

Trust = Trust × λ

Recommended:

λ = 0.99

Implementation:

def decay_trust():

    for agent,data in trust_store.items():

        data["alpha"] *= 0.99
        data["beta"] *= 0.99
9. Trust Update Node

Create LangGraph node:

trust_update_node

Implementation:

def trust_update_node(state: SentinelState):

    verdict = state.get("final_verdict")

    malware = state.get("malware_output", {})
    network = state.get("network_output", {})
    vt = state.get("vt_output", {})
    threatintel = state.get("threatintel_output", {})

    agent_outputs = {
        "malware_agent": malware,
        "network_agent": network,
        "vt_agent": vt,
        "threatintel_agent": threatintel
    }

    for agent,output in agent_outputs.items():

        if not output:
            continue

        agent_verdict = output.get("verdict")

        correct = agent_verdict == verdict

        update_trust(agent, correct)

    decay_trust()

    return {}
10. Router Update

Modify:

sentinelx/core/router.py

Import:

from ..trust.trust_engine import trust_update_node

Add node:

graph.add_node("trust_update", trust_update_node)
11. Update Pipeline

Current pipeline:

agents
 ↓
fusion
 ↓
triage
 ↓
report

New pipeline:

agents
 ↓
fusion
 ↓
triage
 ↓
report
 ↓
trust_update

Implementation:

graph.add_edge("report_agent", "trust_update")
12. Update Orchestrator

Now the orchestrator should use dynamic trust.

Instead of:

trust = AGENT_PROFILES[agent]["trust"]

Use:

trust = compute_trust(agent)

This makes utility adaptive.

13. Logging

Add logging:

logger.info(
 "Updated trust scores: %s",
 trust_store
)
14. Example

Initial trust:

Agent	Trust
MalwareAgent	0.5
NetworkAgent	0.5

After correct detections:

Agent	Trust
MalwareAgent	0.82
NetworkAgent	0.63

Utility increases automatically.

15. Deliverables

After Phase 7 repository contains:

sentinelx/
 ├ trust/
 │   trust_engine.py
 │   __init__.py

Updated files:

router.py
orchestrator.py
state.py
SentinelX After Phase 7

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
 ↓
trust_update