"""
VirusTotal Agent — LangGraph Node
Real VT API lookup with mock fallback.
"""
import requests as http_requests
from ..config import VIRUSTOTAL_API_KEY
from ..models.state import SentinelState

VT_FILE_URL = "https://www.virustotal.com/api/v3/files/{}"
VT_HEADERS = {"x-apikey": VIRUSTOTAL_API_KEY}


def _lookup_hash(file_hash: str) -> dict:
    """Query VirusTotal for a file hash."""
    if not VIRUSTOTAL_API_KEY:
        return _mock(file_hash)
    try:
        resp = http_requests.get(VT_FILE_URL.format(file_hash), headers=VT_HEADERS, timeout=10)
        if resp.status_code == 200:
            stats = resp.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            mal = stats.get("malicious", 0)
            total = sum(stats.values()) if stats else 0
            return {"vt_score": f"{mal}/{total}", "verdict": "malicious" if mal > 5 else "clean", "source": "api"}
        elif resp.status_code == 404:
            return {"vt_score": "0/0", "verdict": "not_found", "source": "api"}
    except http_requests.RequestException:
        pass
    return _mock(file_hash)


def _mock(file_hash: str) -> dict:
    if file_hash == "abcd1234":
        return {"vt_score": "18/70", "verdict": "malicious", "source": "mock"}
    return {"vt_score": "0/70", "verdict": "clean", "source": "mock"}


def vt_node(state: SentinelState) -> dict:
    """Lookup file_hash on VirusTotal."""
    if not state.get("invoke_vt"):
        return {"vt_output": {"vt_score": "N/A", "verdict": "skipped", "source": "skipped"}}

    file_hash = state["log_data"].get("file_hash", "")
    if not file_hash:
        return {"vt_output": {"vt_score": "N/A", "verdict": "no_hash", "source": "skipped"}}

    return {"vt_output": _lookup_hash(file_hash)}
