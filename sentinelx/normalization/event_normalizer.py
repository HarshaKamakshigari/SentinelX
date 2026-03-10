import uuid
import re
from datetime import datetime
from ..models.state import SentinelState


def normalize_structured(log_data: dict) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
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
        "timestamp": datetime.utcnow().isoformat(),
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
        "log_data": normalized,
    }
