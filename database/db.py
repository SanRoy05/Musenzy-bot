"""
database/db.py — Single-file JSON database. Zero external dependencies.

File location:  <project_root>/data/db.json
Data is loaded into memory on first access and written back on every mutation.
An asyncio.Lock serialises all writes to prevent race conditions.

Schema:
{
  "sudo_users": [123456789, 987654321],
  "chats": {
    "-1001234567890": {
      "playmode": "everyone",
      "authusers": [],
      "cleanmode": false
    }
  }
}
"""
from __future__ import annotations

import asyncio
import json
import os

# ── Path setup ─────────────────────────────────────────────────────────────────
# Resolve relative to project root regardless of the working directory.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BASE_DIR, "data", "db.json")

_lock = asyncio.Lock()

_DEFAULTS: dict = {"sudo_users": [], "chats": {}}


# ── Internal I/O helpers (synchronous, cheap for small JSON) ──────────────────

def _load() -> dict:
    """Read db.json and return its contents. Creates the file if absent."""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _save(_DEFAULTS.copy())
        return _DEFAULTS.copy()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        # Back-fill any missing top-level keys.
        for key, val in _DEFAULTS.items():
            data.setdefault(key, val)
        return data
    except (json.JSONDecodeError, OSError):
        # Corrupted file — reset to defaults.
        _save(_DEFAULTS.copy())
        return _DEFAULTS.copy()


def _save(data: dict) -> None:
    """Write *data* to db.json atomically (write-then-replace)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, DB_PATH)  # atomic on POSIX; best-effort on Windows


# ── Initialisation ─────────────────────────────────────────────────────────────

def init() -> None:
    """Create data/ and db.json if they don't exist. Call once at startup."""
    _load()


# ── Sudo users ─────────────────────────────────────────────────────────────────

async def add_sudo(user_id: int) -> None:
    async with _lock:
        data = _load()
        if user_id not in data["sudo_users"]:
            data["sudo_users"].append(user_id)
            _save(data)


async def del_sudo(user_id: int) -> None:
    async with _lock:
        data = _load()
        if user_id in data["sudo_users"]:
            data["sudo_users"].remove(user_id)
            _save(data)


async def get_sudo_users() -> list[int]:
    data = _load()
    return list(data["sudo_users"])


async def is_sudo(user_id: int) -> bool:
    data = _load()
    return user_id in data["sudo_users"]


# ── Per-group helpers ──────────────────────────────────────────────────────────

def _chat(data: dict, chat_id: int) -> dict:
    """Return (and lazily create) the settings dict for *chat_id*."""
    key = str(chat_id)
    if key not in data["chats"]:
        data["chats"][key] = {"playmode": "everyone", "authusers": [], "cleanmode": False}
    return data["chats"][key]


# ── Playmode ───────────────────────────────────────────────────────────────────

async def get_playmode(chat_id: int) -> str:
    """Return "everyone" or "admins" (default: "everyone")."""
    data = _load()
    return _chat(data, chat_id).get("playmode", "everyone")


async def set_playmode(chat_id: int, mode: str) -> None:
    async with _lock:
        data = _load()
        _chat(data, chat_id)["playmode"] = mode
        _save(data)


# ── Auth users ─────────────────────────────────────────────────────────────────

async def get_authusers(chat_id: int) -> list[int]:
    data = _load()
    return list(_chat(data, chat_id).get("authusers", []))


async def add_authuser(chat_id: int, user_id: int) -> None:
    async with _lock:
        data = _load()
        chat = _chat(data, chat_id)
        if user_id not in chat["authusers"]:
            chat["authusers"].append(user_id)
            _save(data)


async def del_authuser(chat_id: int, user_id: int) -> None:
    async with _lock:
        data = _load()
        chat = _chat(data, chat_id)
        if user_id in chat["authusers"]:
            chat["authusers"].remove(user_id)
            _save(data)


# ── Clean mode ─────────────────────────────────────────────────────────────────

async def is_cleanmode(chat_id: int) -> bool:
    data = _load()
    return bool(_chat(data, chat_id).get("cleanmode", False))


async def toggle_cleanmode(chat_id: int) -> bool:
    """Toggle cleanmode; returns the new state (True = on)."""
    async with _lock:
        data = _load()
        chat = _chat(data, chat_id)
        new_state = not bool(chat.get("cleanmode", False))
        chat["cleanmode"] = new_state
        _save(data)
    return new_state
