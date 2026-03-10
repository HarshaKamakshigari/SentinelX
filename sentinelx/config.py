import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the sentinelx directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- API Keys ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")

# --- Model Configuration ---
GEMINI_MODEL: str = "gemini-2.0-flash"

# --- Application ---
APP_NAME: str = "SentinelX"
APP_VERSION: str = "3.0.0"

# --- Threat Intelligence ---
THREAT_INTEL_DATASET: str = str(
    Path(__file__).parent / "data" / "malware_bazaar" / "malware_90ds_filtered.csv"
)

# --- Risk Engine ---
RISK_FLAGS = {
    "encoded_powershell": 0.5,
    "suspicious_lolbin": 0.4,
    "external_connection": 0.2,
    "known_bad_hash": 0.8,
}

# --- Risk Combination (Phase 4) ---
RISK_COMBINATION_WEIGHTS = {
    "heuristic": 0.6,
    "graph": 0.4,
}

RISK_SCALING_POWER = 2

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# --- Validation ---
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to sentinelx/.env")
