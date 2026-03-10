"""
Heuristic Risk Engine — deterministic risk scoring from normalized event signals.
"""
import logging
from ..models.state import SentinelState
from ..config import RISK_FLAGS

logger = logging.getLogger(__name__)

SUSPICIOUS_LOLBINS = [
    "rundll32",
    "mshta",
    "regsvr32",
    "bitsadmin",
    "certutil",
]

KNOWN_BAD_HASHES = {
    "abcd1234",
    "deadbeef",
    "malware_sample_hash",
}


def check_encoded_powershell(cmd: str | None) -> int:
    if not cmd:
        return 0
    cmd = cmd.lower()
    if "powershell" in cmd and "-enc" in cmd:
        return 1
    return 0


def check_lolbins(cmd: str | None) -> int:
    if not cmd:
        return 0
    cmd = cmd.lower()
    for tool in SUSPICIOUS_LOLBINS:
        if tool in cmd:
            return 1
    return 0


def check_external_connection(dest_ip: str | None) -> int:
    if not dest_ip:
        return 0
    return 1


def check_known_bad_hash(file_hash: str | None) -> int:
    if not file_hash:
        return 0
    if file_hash in KNOWN_BAD_HASHES:
        return 1
    return 0


def calculate_risk(flags: dict) -> float:
    total_weight = sum(RISK_FLAGS.values())
    score = 0.0
    for name, value in flags.items():
        weight = RISK_FLAGS.get(name, 0)
        score += weight * value
    return min(1.0, score / total_weight)


def heuristic_risk_node(state: SentinelState) -> dict:
    event = state.get("normalized_event", {})

    command = event.get("command_line")
    dest_ip = event.get("destination_ip")
    file_hash = event.get("file_hash")

    flags = {
        "encoded_powershell": check_encoded_powershell(command),
        "suspicious_lolbin": check_lolbins(command),
        "external_connection": check_external_connection(dest_ip),
        "known_bad_hash": check_known_bad_hash(file_hash),
    }

    risk = calculate_risk(flags)

    logger.info("Heuristic risk score: %.2f flags=%s", risk, flags)

    return {
        "heuristic_risk": risk,
        "risk_flags": flags,
    }
