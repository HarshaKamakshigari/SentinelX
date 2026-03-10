from __future__ import annotations
from typing import TypedDict, Any, Optional

class SentinelState(TypedDict, total=False):
    """Shared state flowing through the LangGraph pipeline."""

    # --- Raw input ---
    raw_log: Optional[str]

    # --- Input ---
    log_data: dict[str, Any]

    # --- Normalized event ---
    normalized_event: dict[str, Any]

    # --- Orchestrator decision ---
    invoke_malware: bool
    invoke_network: bool
    invoke_vt: bool
    invoke_threatintel: bool

    # --- Agent outputs (initialized as empty dicts) ---
    malware_output: dict[str, Any]
    network_output: dict[str, Any]
    vt_output: dict[str, Any]
    threatintel_output: dict[str, Any]

    # --- Triage ---
    severity: str
    confidence: float
    triage_reason: str

    # --- Final ---
    final_report: dict[str, Any]
