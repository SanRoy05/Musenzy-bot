"""
player.py — Playback engine: joins VC as userbot, streams audio/video via PyTgCalls.
"""
from __future__ import annotations

import asyncio
import os
import logging
from typing import Optional

from pyrogram import Client
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream


import config
import queue_manager as qm
from queue_manager import Track

log = logging.getLogger(__name__)

# Singleton: one PyTgCalls instance attached to the userbot.
_call_py: Optional[PyTgCalls] = None
# Mapping chat_id → message_id of the "now playing" bot message (for editing).
_np_messages: dict[int, int] = {}
# Reference to bot client for sending messages.
_bot: Optional[Client] = None


def init(userbot: Client, bot: Client) -> PyTgCalls:
    """Call once at startup. Returns the PyTgCalls instance."""
    global _call_py, _bot
    _bot = bot
    _call_py = PyTgCalls(userbot)

    @_call_py.on_stream_end()
    async def on_stream_end(_, update):
        chat_id = update.chat_id
        state = await qm.get_state(chat_id)
        # Delete the just-played file to save disk space.
        if state.current and state.current.file_path:
            _safe_delete(state.current.file_path)

        next_track = state.next()
        if next_track is None:
            # Queue exhausted — leave VC.
            await _leave(chat_id)
            if _bot:
                try:
                    await _bot.send_message(chat_id, "✅ Queue finished. Left the voice chat.")
                except Exception:
                    pass
        else:
            await _stream(chat_id, next_track)

    return _call_py


# ── internal helpers ───────────────────────────────────────────────────────────

def _safe_delete(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as exc:
        log.warning("Could not delete %s: %s", path, exc)


async def _stream(chat_id: int, track: Track):
    """Start or switch the stream for chat_id."""
    path = track.file_path or track.url
    
    try:
        # play() automatically handles both join and change_stream in py-tgcalls 2.2.x
        await _call_py.play(chat_id, MediaStream(path))
    except Exception as exc:
        if "GroupCallNotFound" in str(type(exc)):
            log.warning("No active group call in %s", chat_id)
            if _bot:
                await _bot.send_message(chat_id, "❌ No active voice chat found. Please start one first.")
        else:
            log.exception("Stream error in %s: %s", chat_id, exc)
            if _bot:
                await _bot.send_message(chat_id, f"❌ Playback error: {exc}")
        return

    # Announce now-playing.
    if _bot:
        from ytdl import fmt_duration
        dur = fmt_duration(track.duration)
        text = (
            f"🎵 **Now Playing**\n"
            f"[{track.title}]({track.url})\n"
            f"⏱ `{dur}` | 🔊 Requested by <a href='tg://user?id={track.requested_by}'>"
            f"user</a>"
        )
        try:
            msg = await _bot.send_message(chat_id, text, disable_web_page_preview=True)
            _np_messages[chat_id] = msg.id
        except Exception:
            pass


async def _leave(chat_id: int):
    try:
        await _call_py.leave_group_call(chat_id)
    except Exception:
        pass


# ── public API ─────────────────────────────────────────────────────────────────

async def play(chat_id: int, track: Track) -> str:
    """
    Add track to queue. If nothing is playing, start immediately.
    Returns a status string for the bot to relay.
    """
    state = await qm.get_state(chat_id)
    async with state._lock:
        if state.is_playing:
            added = state.add(track)
            if not added:
                return f"❌ Queue is full ({config.MAX_QUEUE_SIZE} tracks max)."
            pos = len(state.queue)
            return f"✅ Added to queue (position #{pos}): **{track.title}**"
        else:
            state.current = track
            state.is_playing = True
    await _stream(chat_id, track)
    return ""   # Caller sends "now playing" from the stream itself.


async def pause(chat_id: int) -> str:
    try:
        await _call_py.pause_stream(chat_id)
        return "⏸ Paused."
    except Exception as e:
        return f"❌ {e}"


async def resume(chat_id: int) -> str:
    try:
        await _call_py.resume_stream(chat_id)
        return "▶️ Resumed."
    except Exception as e:
        return f"❌ {e}"


async def skip(chat_id: int) -> str:
    state = await qm.get_state(chat_id)
    if state.current and state.current.file_path:
        _safe_delete(state.current.file_path)
    next_track = state.next()
    if next_track is None:
        await _leave(chat_id)
        return "⏭ Skipped. Queue empty — left the voice chat."
    await _stream(chat_id, next_track)
    return f"⏭ Skipped. Now playing: **{next_track.title}**"


async def stop(chat_id: int) -> str:
    state = await qm.get_state(chat_id)
    if state.current and state.current.file_path:
        _safe_delete(state.current.file_path)
    for t in state.queue:
        if t.file_path:
            _safe_delete(t.file_path)
    state.clear()
    await _leave(chat_id)
    return "⏹ Stopped and cleared queue. Left the voice chat."


async def set_volume(chat_id: int, vol: int) -> str:
    vol = max(0, min(200, vol))
    try:
        await _call_py.change_volume_call(chat_id, vol)
        state = await qm.get_state(chat_id)
        state.volume = vol
        return f"🔊 Volume set to **{vol}**."
    except Exception as e:
        return f"❌ {e}"


async def toggle_loop(chat_id: int) -> str:
    state = await qm.get_state(chat_id)
    state.loop = not state.loop
    mode = "enabled 🔁" if state.loop else "disabled"
    return f"Loop {mode}."


def get_pytgcalls() -> Optional[PyTgCalls]:
    return _call_py
