"""
queue_manager.py — In-memory per-chat queue + playback state.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional

import config


@dataclass
class Track:
    title: str
    url: str          # direct stream URL (or file path after download)
    duration: int     # seconds
    thumbnail: str    # thumbnail URL
    requested_by: int  # user_id
    is_video: bool = False
    file_path: Optional[str] = None  # local path if downloaded


@dataclass
class ChatState:
    queue: list[Track] = field(default_factory=list)
    current: Optional[Track] = None
    loop: bool = False
    volume: int = field(default_factory=lambda: config.DEFAULT_VOLUME)
    is_playing: bool = False
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    # ── queue helpers ──────────────────────────────────────────────────────────
    def add(self, track: Track) -> bool:
        """Return False if queue is full."""
        if len(self.queue) >= config.MAX_QUEUE_SIZE:
            return False
        self.queue.append(track)
        return True

    def next(self) -> Optional[Track]:
        """Pop next track; handle loop."""
        if self.loop and self.current:
            return self.current
        if not self.queue:
            self.current = None
            self.is_playing = False
            return None
        self.current = self.queue.pop(0)
        self.is_playing = True
        return self.current

    def clear(self):
        self.queue.clear()
        self.current = None
        self.is_playing = False
        self.loop = False


# Global registry: chat_id → ChatState
_states: dict[int, ChatState] = {}
_registry_lock = asyncio.Lock()


async def get_state(chat_id: int) -> ChatState:
    async with _registry_lock:
        if chat_id not in _states:
            _states[chat_id] = ChatState()
        return _states[chat_id]


async def remove_state(chat_id: int):
    async with _registry_lock:
        _states.pop(chat_id, None)
