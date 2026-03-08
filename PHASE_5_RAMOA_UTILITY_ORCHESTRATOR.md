SentinelX v4 – Phase 5 Implementation
RAMOA Utility-Based Orchestrator

Version: SentinelX v4 – Phase 5

Goal:

Replace the static routing logic in SentinelX with a utility-based orchestrator that decides which agents to run based on risk, agent trust, and execution cost.

This transforms SentinelX into a Risk-Adaptive Multi-Agent SOC system.

1. Why This Phase Exists

Before Phase 5, SentinelX routing logic is mostly:

log → orchestrator → agents

Agents are invoked using simple rules such as:

• command_line contains suspicious text
• destination_ip exists
• file_hash exists

This is not resource aware.

RAMOA introduces expected utility.

Agents run only if they are worth the cost.

2. Expected Utility Formula

RAMOA defines:

Utility(Ai) = (ScaledRisk × TrustScore[Ai]) − ExecutionCost[Ai]

Where:

Variable	Meaning
ScaledRisk	risk produced in Phase 4
TrustScore	reliability of the agent
ExecutionCost	compute cost of running agent
3. Execution Decision

An agent runs only if:

Utility(Ai) > τ

Where:

τ = 0.1

This threshold avoids running agents when risk is too low.

4. SentinelX Pipeline After Phase 5

Before:

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

After Phase 5 the orchestrator becomes the RAMOA brain:

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
5. Agent Profiles

Add agent metadata to config.py.

Modify:

sentinelx/config.py

Add:

AGENT_PROFILES = {

    "malware_agent": {
        "trust": 0.8,
        "cost": 0.05
    },

    "network_agent": {
        "trust": 0.7,
        "cost": 0.04
    },

    "threatintel_agent": {
        "trust": 0.9,
        "cost": 0.01
    },

    "vt_agent": {
        "trust": 0.85,
        "cost": 0.20
    }

}

UTILITY_THRESHOLD = 0.1

These values represent:

Agent	Reason
ThreatIntel	cheap local lookup
Network	cheap
Malware	moderate
VirusTotal	expensive external API
6. Utility Calculation Module

Create new module:

sentinelx/orchestration/utility_engine.py

Implementation:

from ..config import AGENT_PROFILES, UTILITY_THRESHOLD


def compute_utility(agent_name, scaled_risk):

    profile = AGENT_PROFILES.get(agent_name, {})

    trust = profile.get("trust", 0.5)

    cost = profile.get("cost", 0.1)

    utility = (scaled_risk * trust) - cost

    return utility


def should_invoke(agent_name, scaled_risk):

    utility = compute_utility(agent_name, scaled_risk)

    return utility > UTILITY_THRESHOLD, utility
7. Update Orchestrator Agent

Modify:

sentinelx/agents/orchestrator.py

Replace existing invocation logic.

Import utility engine
from ..orchestration.utility_engine import should_invoke
Utility-Based Invocation

Example implementation:

def orchestrator_node(state: SentinelState):

    log_data = state["log_data"]

    scaled_risk = state.get("scaled_risk", 0)

    invoke_malware, malware_util = should_invoke(
        "malware_agent",
        scaled_risk
    )

    invoke_network, network_util = should_invoke(
        "network_agent",
        scaled_risk
    )

    invoke_threatintel, ti_util = should_invoke(
        "threatintel_agent",
        scaled_risk
    )

    invoke_vt, vt_util = should_invoke(
        "vt_agent",
        scaled_risk
    )

    return {
        "invoke_malware": invoke_malware,
        "invoke_network": invoke_network,
        "invoke_threatintel": invoke_threatintel,
        "invoke_vt": invoke_vt,

        "agent_utilities": {
            "malware": malware_util,
            "network": network_util,
            "threatintel": ti_util,
            "vt": vt_util
        }
    }
8. Update SentinelState

Modify:

sentinelx/models/state.py

Add:

agent_utilities: dict

Example:

scaled_risk: float
agent_utilities: dict
9. Logging

Add logging for transparency.

logger.info(
 "Agent utilities: %s",
 agent_utilities
)

This allows SOC analysts to understand why agents ran.

10. Example Scenario

Event:

powershell.exe -enc ABC

Risk signals:

heuristic_risk = 0.5
graph_score = 0.6

Estimated risk:

0.56

Scaled risk:

0.31
Utility Calculation

Malware agent:

(0.31 × 0.8) − 0.05 = 0.198

Run.

Network agent:

(0.31 × 0.7) − 0.04 = 0.177

Run.

VirusTotal:

(0.31 × 0.85) − 0.2 = 0.06

Below threshold → skip.

11. Result

Only useful agents run.

Benefits:

Benefit	Description
Reduced cost	fewer expensive API calls
Faster SOC response	fewer unnecessary analyses
Adaptive investigation	high-risk events trigger deeper analysis
12. Deliverables

After Phase 5 repository contains:

sentinelx/
 ├ orchestration/
 │   utility_engine.py

Updated files:

config.py
orchestrator.py
state.py
13. SentinelX After Phase 5

The system becomes a risk-adaptive multi-agent SOC.

Pipeline:

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
triage
 ↓
report