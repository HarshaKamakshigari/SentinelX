"""
Threat Intelligence Index
Provides high-level query interface for the threat intel knowledge base.
Supports hash lookup, malware family identification, and detection confidence.
"""
from typing import Dict, Any, Optional
from .loader import get_index, load_dataset, is_loaded


def lookup_hash(file_hash: str) -> Dict[str, Any]:
    """
    Look up a file hash in the threat intelligence knowledge base.

    Args:
        file_hash: SHA256, MD5, or SHA1 hash to look up.

    Returns:
        Dict with threat intelligence data if found, or a no-match result.
    """
    if not is_loaded():
        load_dataset()

    index = get_index()
    normalized = file_hash.strip().lower()
    record = index.get(normalized)

    if record is None:
        return {
            "threat_match": False,
        }

    return {
        "threat_match": True,
        "malware_family": record.get("malware_family", "Unknown"),
        "file_name": record.get("file_name", ""),
        "file_type": record.get("file_type", ""),
        "mime_type": record.get("mime_type", ""),
        "vt_percent": record.get("vt_percent"),
        "ssdeep": record.get("ssdeep", ""),
        "tlsh": record.get("tlsh", ""),
        "source": "MalwareBazaar",
    }


def get_malware_family(file_hash: str) -> Optional[str]:
    """
    Get the malware family name for a given hash.

    Returns:
        Malware family string or None if not found.
    """
    result = lookup_hash(file_hash)
    if result.get("threat_match"):
        return result.get("malware_family")
    return None


def get_detection_confidence(file_hash: str) -> Optional[float]:
    """
    Get the VirusTotal detection percentage from the KB for a given hash.

    Returns:
        Float (0-100) or None if not found or unavailable.
    """
    result = lookup_hash(file_hash)
    if result.get("threat_match"):
        return result.get("vt_percent")
    return None
