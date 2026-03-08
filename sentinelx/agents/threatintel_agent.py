"""
Threat Intelligence Agent — LangGraph Node
Checks file hashes against the local MalwareBazaar threat intelligence KB.
Enriches the analysis state with malware family classification.
"""
import logging
from ..models.state import SentinelState
from ..threat_intel.index import lookup_hash

logger = logging.getLogger(__name__)


def threatintel_node(state: SentinelState) -> dict:
    """
    Look up file hash in the local threat intelligence knowledge base.

    Input: file_hash from log_data
    Output: threat intel enrichment (malware family, file type, VT %, source)
    """
    skip = {"threatintel_output": {"threat_match": False}}

    if not state.get("invoke_threatintel"):
        return skip

    file_hash = state["log_data"].get("file_hash", "")
    if not file_hash:
        return skip

    try:
        result = lookup_hash(file_hash)
    except Exception as exc:
        logger.error("Threat intel lookup failed: %s", exc)
        return skip

    if result.get("threat_match"):
        logger.info(
            "Threat intel match: hash=%s family=%s vt=%.1f%%",
            file_hash[:16],
            result.get("malware_family", "Unknown"),
            result.get("vt_percent") or 0.0,
        )
    else:
        logger.info("No threat intel match for hash: %s", file_hash[:16])

    return {"threatintel_output": result}
