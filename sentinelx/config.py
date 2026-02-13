import os
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
APP_VERSION: str = "2.0.0"

# --- Validation ---
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to sentinelx/.env")
