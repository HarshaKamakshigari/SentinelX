import uuid
import re
import shlex
from datetime import datetime, timezone
from ..models.state import SentinelState


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_process_name(command_line: str | None) -> str | None:
    if not command_line:
        return None

    try:
        tokens = shlex.split(command_line, posix=False)
    except ValueError:
        tokens = command_line.split()

    if not tokens:
        return None

    executable = tokens[0].strip().strip("\"'")
    if not executable:
        return None

    return re.split(r"[\\/]", executable)[-1] or None


def normalize_structured(log_data: dict) -> dict:
    command_line = log_data.get("command_line")

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": _timestamp(),
        "host": log_data.get("host"),
        "event_type": log_data.get("event_type"),
        "process_name": log_data.get("process_name") or _extract_process_name(command_line),
        "parent_process": log_data.get("parent_process"),
        "command_line": command_line,
        "source_ip": log_data.get("source_ip"),
        "destination_ip": log_data.get("destination_ip"),
        "file_hash": log_data.get("file_hash"),
        "file_name": log_data.get("file_name"),
        "user_id": log_data.get("user_id"),
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
        "timestamp": _timestamp(),
        "host": host,
        "event_type": "raw_event",
        "process_name": _extract_process_name(command or raw_log),
        "parent_process": None,
        "command_line": command,
        "source_ip": None,
        "destination_ip": dest_ip,
        "file_hash": None,
        "file_name": None,
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
