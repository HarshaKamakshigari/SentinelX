"""
In-memory incident case store.
Stores all processed incidents for dashboard retrieval.
"""
from typing import List, Dict, Any
import threading

_lock = threading.Lock()
_incidents: List[Dict[str, Any]] = []


def save_incident(report: Dict[str, Any]) -> None:
    """Append a processed incident report to the store."""
    with _lock:
        _incidents.append(report)


def get_all_incidents() -> List[Dict[str, Any]]:
    """Return all incidents, newest first."""
    with _lock:
        return list(reversed(_incidents))


def clear_incidents() -> None:
    """Clear all stored incidents."""
    with _lock:
        _incidents.clear()
