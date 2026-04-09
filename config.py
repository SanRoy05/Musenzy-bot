"""
config.py — Load all configuration from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


# ── Telegram credentials ──────────────────────────────────────────────────────
API_ID: int = _int("API_ID", 0)
API_HASH: str = os.getenv("API_HASH", "")
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
SESSION_STRING: str = os.getenv("SESSION_STRING", "")

# ── Access control ────────────────────────────────────────────────────────────
# Single owner — highest permission level (Level 1).
OWNER_ID: int = _int("OWNER_ID", 0)

# ── MongoDB ───────────────────────────────────────────────────────────────────
# Removed in favor of local JSON DB.

# ── Logger chat ───────────────────────────────────────────────────────────────
# Removed.

# ── Player settings ───────────────────────────────────────────────────────────
MAX_QUEUE_SIZE: int = _int("MAX_QUEUE_SIZE", 20)
DEFAULT_VOLUME: int = _int("DEFAULT_VOLUME", 100)
DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "/tmp/musenzy")

# ── Validate mandatory fields at import time ──────────────────────────────────
_REQUIRED = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN,
    "SESSION_STRING": SESSION_STRING,
    "OWNER_ID": OWNER_ID,
}
for _name, _val in _REQUIRED.items():
    if not _val:
        raise RuntimeError(f"[config] Missing required env var: {_name}")

# Ensure download directory exists.
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
