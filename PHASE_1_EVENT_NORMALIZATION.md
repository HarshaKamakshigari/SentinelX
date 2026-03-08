SentinelX v4 – Phase 1 Implementation
Event Normalization Engine

Version: SentinelX v4 – Phase 1

Goal:

Introduce a canonical Event Normalization Layer that converts all incoming telemetry into a standardized internal event object before it enters the LangGraph pipeline.

This is the first architectural step required for RAMOA integration.

1. Problem

Currently SentinelX directly consumes structured logs like:

{
 "host": "test-pc",
 "event_type": "file_create",
 "file_hash": "abcd1234"
}

However real SOC systems ingest:

• Syslog
• Windows Event XML
• Firewall logs
• CSV telemetry
• EDR alerts

These formats are inconsistent.

RAMOA requires a normalized event object before risk scoring and orchestration.

2. Phase 1 Objective

Implement an Event Normalization Layer that:

Accepts raw or structured logs

Extracts relevant security attributes

Converts them into a canonical Event object

Passes this event into the LangGraph pipeline

3. Expected Pipeline After Phase 1

Current pipeline:

log → orchestrator → agents → triage → report

New pipeline:

log → normalizer → orchestrator → agents → triage → report
4. New Module Structure

Create a new directory:

sentinelx/
 ├── normalization/
 │     __init__.py
 │     event_normalizer.py
5. Canonical Event Schema

Create a normalized event object.

Add a new model:

sentinelx/models/event_model.py
Implementation
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NormalizedEvent(BaseModel):

    event_id: str
    timestamp: datetime

    host: Optional[str]

    user_id: Optional[str]

    process_name: Optional[str]
    command_line: Optional[str]

    source_ip: Optional[str]
    destination_ip: Optional[str]

    file_hash: Optional[str]

    event_type: Optional[str]
6. Update SentinelState

Modify:

sentinelx/models/state.py

Add new fields:

normalized_event: dict
raw_log: Optional[str]

Final relevant section:

class SentinelState(TypedDict, total=False):

    raw_log: Optional[str]

    log_data: dict[str, Any]

    normalized_event: dict[str, Any]
7. Update SecurityLog Model

Modify:

sentinelx/models/log_model.py

Add support for raw logs.

class SecurityLog(BaseModel):

    host: Optional[str] = None
    event_type: Optional[str] = None

    command_line: Optional[str] = None
    file_hash: Optional[str] = None
    destination_ip: Optional[str] = None

    raw_log: Optional[str] = None
8. Event Normalizer Node

Create file:

sentinelx/normalization/event_normalizer.py

Implementation:

import uuid
import re
from datetime import datetime
from ..models.state import SentinelState


def normalize_structured(log_data: dict) -> dict:

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow(),
        "host": log_data.get("host"),
        "event_type": log_data.get("event_type"),
        "process_name": None,
        "command_line": log_data.get("command_line"),
        "source_ip": None,
        "destination_ip": log_data.get("destination_ip"),
        "file_hash": log_data.get("file_hash"),
        "user_id": None,
    }


def normalize_raw(raw_log: str) -> dict:

    host = None
    command = None
    dest_ip = None

    ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw_log)

    if ip_match:
        dest_ip = ip_match.group()

    if "powershell" in raw_log.lower():
        command = raw_log

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow(),
        "host": host,
        "event_type": "raw_event",
        "process_name": None,
        "command_line": command,
        "source_ip": None,
        "destination_ip": dest_ip,
        "file_hash": None,
        "user_id": None,
    }


def normalizer_node(state: SentinelState) -> dict:

    log_data = state.get("log_data", {})
    raw_log = log_data.get("raw_log")

    if raw_log:
        normalized = normalize_raw(raw_log)
    else:
        normalized = normalize_structured(log_data)

    return {
        "normalized_event": normalized,
        "log_data": normalized
    }
9. Update LangGraph Router

Modify:

sentinelx/core/router.py

Add new node.

Import
from ..normalization.event_normalizer import normalizer_node
Add Node
graph.add_node("normalizer", normalizer_node)
Update Flow

Current:

graph.set_entry_point("orchestrator")

Change to:

graph.set_entry_point("normalizer")
Add Edge
graph.add_edge("normalizer", "orchestrator")
Final Pipeline
normalizer
↓
orchestrator
↓
malware_agent
↓
network_agent
↓
threatintel_agent
↓
vt_agent
↓
triage
↓
report
10. Update Main API

Modify:

sentinelx/main.py

No major changes required.

Just confirm:

initial_state = {
    "log_data": log.model_dump()
}

The normalizer will convert it.

11. Testing

Start server.

uvicorn sentinelx.main:app --port 8001
Test Structured Event
POST /ingest
{
 "host": "finance-01",
 "event_type": "process_creation",
 "command_line": "powershell.exe -enc ABC123"
}

Expected:

Normal event processed successfully.

Test Raw Log
POST /ingest
{
 "raw_log": "2026-01-01 user ran powershell.exe -enc ABC connecting to 45.77.12.90"
}

Expected:

Normalizer extracts:

command_line
destination_ip
12. Expected Outcome

After Phase 1:

SentinelX supports:

• structured logs
• raw logs
• canonical event schema

This prepares the system for:

Phase 2 – Heuristic Risk Engine

Phase 3 – Graph Intelligence

Phase 4 – RAMOA Orchestration

13. Deliverables

After Cursor finishes Phase 1 the repo must contain:

sentinelx/
 ├ normalization/
 │   event_normalizer.py
 │   __init__.py
 │
 ├ models/
 │   event_model.py
 │
 ├ core/
 │   router.py (updated)