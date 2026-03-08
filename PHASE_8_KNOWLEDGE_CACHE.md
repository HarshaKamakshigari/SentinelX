SentinelX v4 – Phase 8 Implementation
Knowledge Cache & Fast Path Engine

Version: SentinelX v4 – Phase 8

Goal:

Implement a knowledge cache that stores previously analyzed events and returns instant verdicts when identical events appear again.

This reduces:

• unnecessary agent execution
• expensive LLM calls
• VirusTotal API usage

It also enables knowledge reuse, a core RAMOA feature.

1. Why This Layer Exists

Without caching:

Event → Full pipeline → Agents → Fusion → Report

Even if the exact same event occurs 1000 times.

With RAMOA caching:

Event → Cache Check
         ↓
      Cache Hit → Instant Verdict
         ↓
      Cache Miss → Full Pipeline

This is called the fast path.

2. SentinelX Pipeline After Phase 8

Final architecture:

log
 ↓
normalizer
 ↓
knowledge_cache
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
 ↓
cache_store
3. New Module

Create directory:

sentinelx/
 ├ cache/
 │   __init__.py
 │   event_cache.py
4. Cache Data Structure

Cache key must uniquely identify an event.

We create an event signature.

Example:

event_signature = hash(
    sorted(event_fields)
)
5. Cache Structure
event_cache = {

 "event_hash": {
     "verdict": "malicious",
     "confidence": 0.82,
     "timestamp": 1710000000,
     "ttl": 3600
 }

}

TTL ensures results expire over time.

6. Cache Engine

Create file:

sentinelx/cache/event_cache.py

Implementation:

import time
import hashlib

event_cache = {}

CACHE_TTL = 3600
7. Event Signature

Add function:

def event_signature(event):

    key = str(sorted(event.items()))

    return hashlib.sha256(key.encode()).hexdigest()
8. Cache Lookup

Add function:

def lookup_cache(event):

    sig = event_signature(event)

    entry = event_cache.get(sig)

    if not entry:
        return None

    now = time.time()

    if now > entry["timestamp"] + entry["ttl"]:
        del event_cache[sig]
        return None

    return entry
9. Cache Store

Add function:

def store_cache(event, verdict, confidence):

    sig = event_signature(event)

    event_cache[sig] = {
        "verdict": verdict,
        "confidence": confidence,
        "timestamp": time.time(),
        "ttl": CACHE_TTL
    }
10. Cache Check Node

Create LangGraph node.

cache_lookup_node

Implementation:

from ..models.state import SentinelState
from .event_cache import lookup_cache

def cache_lookup_node(state: SentinelState):

    event = state.get("log_data", {})

    result = lookup_cache(event)

    if result:

        return {
            "cache_hit": True,
            "final_confidence": result["confidence"],
            "final_verdict": result["verdict"]
        }

    return {"cache_hit": False}
11. Cache Store Node

Add node to store results after analysis.

from .event_cache import store_cache

def cache_store_node(state: SentinelState):

    event = state.get("log_data", {})

    verdict = state.get("final_verdict")

    confidence = state.get("final_confidence")

    if verdict:

        store_cache(event, verdict, confidence)

    return {}
12. Update SentinelState

Modify:

sentinelx/models/state.py

Add fields:

cache_hit: bool
13. Router Update

Modify:

sentinelx/core/router.py

Import:

from ..cache.event_cache import cache_lookup_node
from ..cache.event_cache import cache_store_node

Add nodes:

graph.add_node("cache_lookup", cache_lookup_node)
graph.add_node("cache_store", cache_store_node)
14. Pipeline Integration

Modify pipeline.

Before:

normalizer
 ↓
heuristic_risk

After:

normalizer
 ↓
cache_lookup
 ↓
heuristic_risk

Implementation:

graph.add_edge("normalizer", "cache_lookup")
graph.add_edge("cache_lookup", "heuristic_risk")
15. Early Exit Logic

If cache hit:

Skip agents.

Add condition in router or orchestrator.

Example:

if state.get("cache_hit"):
    return END
16. Store Cache After Report

Add edge:

graph.add_edge("trust_update", "cache_store")
17. Logging

Add logging:

logger.info("Cache hit for event")

logger.info("Stored event in cache")
18. Example

First event:

powershell.exe -enc ABC

Pipeline runs fully.

Result stored in cache.

Second identical event:

powershell.exe -enc ABC

Pipeline:

normalizer
 ↓
cache_lookup
 ↓
CACHE HIT
 ↓
instant verdict

Agents are not executed.

19. Deliverables

New module:

sentinelx/cache/
    event_cache.py

Updated files:

router.py
state.py
report_agent.py
20. SentinelX v4 Final Architecture

Your final system:

log
 ↓
normalizer
 ↓
knowledge_cache
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
 ↓
cache_store
What SentinelX v4 Now Achieves

Your system now includes:

SOC Automation

✔ agent orchestration
✔ automated investigation
✔ structured reporting

RAMOA Features

✔ risk-adaptive investigation
✔ graph behavioral analysis
✔ utility-based agent invocation
✔ trust learning
✔ confidence fusion
✔ knowledge reuse

What You Built

SentinelX v4 is now:

A Risk-Adaptive Multi-Agent Security Operations Center (SOC) Framework with Graph Intelligence and Trust-Aware Orchestration