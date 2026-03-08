"""
Threat Intelligence Dataset Loader
Parses the MalwareBazaar CSV dataset and builds an in-memory lookup table.
Maps sha256_hash → malware metadata for instant hash lookups.
"""
import csv
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default dataset path relative to the sentinelx package root
_DEFAULT_DATASET = Path(__file__).resolve().parent.parent / "data" / "malware_bazaar" / "malware_90ds_filtered.csv"

# In-memory lookup table: sha256 → metadata dict
_hash_index: Dict[str, Dict[str, Any]] = {}
_loaded: bool = False


def _parse_vt_percent(raw: str) -> Optional[float]:
    """Safely parse the vtpercent field to a float."""
    raw = raw.strip()
    if not raw or raw.lower() == "n/a":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _extract_malware_family(signature: str) -> str:
    """Extract malware family from the 'signature' column."""
    sig = signature.strip()
    if not sig or sig.lower() == "n/a":
        return "Unknown"
    return sig


def load_dataset(dataset_path: Optional[str] = None) -> int:
    """
    Load the malware dataset CSV into the in-memory index.

    Args:
        dataset_path: Optional path to the CSV. Uses default if not provided.

    Returns:
        Number of records loaded.
    """
    global _hash_index, _loaded

    path = Path(dataset_path) if dataset_path else _DEFAULT_DATASET

    if not path.exists():
        logger.warning("Threat intel dataset not found at %s", path)
        _loaded = True  # Mark as loaded (empty) to avoid repeated attempts
        return 0

    count = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sha256 = row.get("sha256_hash", "").strip()
                if not sha256:
                    continue

                record = {
                    "sha256": sha256,
                    "md5": row.get("md5_hash", "").strip(),
                    "sha1": row.get("sha1_hash", "").strip(),
                    "malware_family": _extract_malware_family(row.get("signature", "")),
                    "file_name": row.get("file_name", "").strip(),
                    "file_type": row.get("file_type_guess", "").strip(),
                    "mime_type": row.get("mime_type", "").strip(),
                    "vt_percent": _parse_vt_percent(row.get("vtpercent", "")),
                    "ssdeep": row.get("ssdeep", "").strip(),
                    "tlsh": row.get("tlsh", "").strip(),
                    "reporter": row.get("reporter", "").strip(),
                    "date": row.get("date", "").strip(),
                }

                # Index by sha256 (primary key)
                _hash_index[sha256.lower()] = record

                # Also index by md5 and sha1 for broader lookup
                md5 = record["md5"]
                sha1 = record["sha1"]
                if md5:
                    _hash_index[md5.lower()] = record
                if sha1:
                    _hash_index[sha1.lower()] = record

                count += 1

    except Exception as exc:
        logger.error("Failed to load threat intel dataset: %s", exc)
        _loaded = True
        return 0

    _loaded = True
    logger.info("Threat intel KB loaded: %d malware records indexed", count)
    return count


def get_index() -> Dict[str, Dict[str, Any]]:
    """Return the raw in-memory hash index."""
    if not _loaded:
        load_dataset()
    return _hash_index


def is_loaded() -> bool:
    """Check whether the dataset has been loaded."""
    return _loaded


def record_count() -> int:
    """Return the number of unique sha256 records (approximate)."""
    if not _loaded:
        load_dataset()
    # Divide by ~3 because we index by sha256, md5, and sha1
    return len(_hash_index) // 3 if _hash_index else 0
