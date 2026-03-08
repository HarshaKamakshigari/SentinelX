SentinelX v4 – Phase 2 Implementation
Heuristic Risk Engine

Version: SentinelX v4 – Phase 2

Goal:

Introduce a deterministic heuristic risk scoring engine that evaluates how suspicious an event is before invoking heavy agents.

This is the first part of RAMOA's risk estimation layer.

1. Why This Layer Exists

Currently SentinelX:

log → orchestrator → agents

Every event may trigger LLM analysis or external APIs.

This is inefficient.

RAMOA introduces risk estimation before investigation.

So the pipeline becomes:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
orchestrator
 ↓
agents
2. Phase 2 Objective

Compute a baseline risk score between 0 and 1 using security heuristics.

Example suspicious signals:

Signal	Example	Risk
Encoded PowerShell	powershell -enc	high
Known bad IP	TOR / malicious IP	medium
Malware hash	known malware sample	very high
Suspicious port	unusual port	low

These signals produce HeuristicRisk.

3. New Module

Create directory:

sentinelx/
 ├ risk/
 │    __init__.py
 │    heuristic_risk.py
4. Risk Flags Configuration

Modify:

sentinelx/config.py

Add:

RISK_FLAGS = {

    "encoded_powershell": 0.5,

    "suspicious_lolbin": 0.4,

    "known_bad_ip": 0.4,

    "known_bad_hash": 0.8,

    "external_connection": 0.2,

}

These are weights.

Higher weight → stronger signal.

5. Heuristic Detection Logic

Create file:

sentinelx/risk/heuristic_risk.py

Implementation:

from ..models.state import SentinelState
from ..config import RISK_FLAGS


SUSPICIOUS_LOLBINS = [
    "rundll32",
    "mshta",
    "regsvr32",
    "bitsadmin",
    "certutil"
]


def check_encoded_powershell(cmd):

    if not cmd:
        return 0

    cmd = cmd.lower()

    if "powershell" in cmd and "-enc" in cmd:
        return 1

    return 0


def check_lolbins(cmd):

    if not cmd:
        return 0

    cmd = cmd.lower()

    for tool in SUSPICIOUS_LOLBINS:
        if tool in cmd:
            return 1

    return 0


def check_external_connection(dest_ip):

    if not dest_ip:
        return 0

    return 1


def check_bad_hash(threatintel):

    if threatintel.get("threat_match"):
        return 1

    return 0
6. Risk Calculation

Add scoring function:

def calculate_risk(flags):

    total_weight = sum(RISK_FLAGS.values())

    score = 0

    for name, value in flags.items():

        weight = RISK_FLAGS.get(name, 0)

        score += weight * value

    risk = min(1.0, score / total_weight)

    return risk
7. Heuristic Risk Node

Add LangGraph node:

def heuristic_risk_node(state: SentinelState) -> dict:

    log = state.get("log_data", {})

    threatintel = state.get("threatintel_output", {})

    command = log.get("command_line")

    dest_ip = log.get("destination_ip")

    flags = {}

    flags["encoded_powershell"] = check_encoded_powershell(command)

    flags["suspicious_lolbin"] = check_lolbins(command)

    flags["external_connection"] = check_external_connection(dest_ip)

    flags["known_bad_hash"] = check_bad_hash(threatintel)

    risk = calculate_risk(flags)

    return {
        "heuristic_risk": risk,
        "risk_flags": flags
    }
8. Update SentinelState

Modify:

sentinelx/models/state.py

Add fields:

heuristic_risk: float

risk_flags: dict
9. Update Router Pipeline

Modify:

sentinelx/core/router.py

Import node:

from ..risk.heuristic_risk import heuristic_risk_node

Add node:

graph.add_node("heuristic_risk", heuristic_risk_node)
10. Update Pipeline Order

Current pipeline after Phase 1:

normalizer
 ↓
orchestrator
 ↓
agents

Change to:

normalizer
 ↓
heuristic_risk
 ↓
orchestrator
 ↓
agents

Implementation:

graph.set_entry_point("normalizer")

graph.add_edge("normalizer", "heuristic_risk")

graph.add_edge("heuristic_risk", "orchestrator")
11. Orchestrator Upgrade

Update:

sentinelx/agents/orchestrator.py

Add risk awareness.

Example logic:

risk = state.get("heuristic_risk", 0)

if risk < 0.2:
    return {
        "invoke_malware": False,
        "invoke_network": False,
        "invoke_vt": False,
        "invoke_threatintel": False
    }

Low-risk events skip expensive agents.

12. Expected Behavior

Example event:

powershell.exe -enc ABC123

Flags:

encoded_powershell = 1
lolbin = 0
external_connection = 0
known_bad_hash = 0

Risk:

HeuristicRisk ≈ 0.38

Agents invoked.

Example event:

notepad.exe report.txt

Flags:

all = 0

Risk:

HeuristicRisk = 0

Agents skipped.

13. Logging

Add logging:

logger.info(
 "Heuristic risk score: %.2f flags=%s",
 risk,
 flags
)
14. Testing

Test event:

POST /ingest
{
 "host": "finance-01",
 "event_type": "process_creation",
 "command_line": "powershell.exe -enc JAB..."
}

Expected logs:

Heuristic risk score: 0.45

Pipeline continues.

15. Deliverables

After Phase 2 the repository must contain:

sentinelx/
 ├ risk/
 │   heuristic_risk.py
 │   __init__.py

Updated files:

config.py
router.py
state.py
orchestrator.py
16. System State After Phase 2

SentinelX pipeline becomes:

log
 ↓
normalizer
 ↓
heuristic_risk
 ↓
orchestrator
 ↓
agents
 ↓
triage
 ↓
report

This enables risk-based investigation.