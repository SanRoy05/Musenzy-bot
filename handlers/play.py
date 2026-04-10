"""
handlers/play.py — /play and /vplay commands with playmode enforcement.

Playmode logic:
    "admins"   → require is_admin()  before playing
    "everyone" → any group member can play
"""
from __future__ import annotations

import logging
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

import config
import player
import queue_manager as qm
from queue_manager import Track
from permissions import is_admin
from database.db import get_playmode
from ytdl import (
    search_youtube,
    download_audio,
    download_video,
    get_info,
    get_playlist_entries,
    fmt_duration,
    is_url,
)

log = logging.getLogger(__name__)

# key = f"{chat_id}:{user_id}", value = list[dict] (search results)
_pending_searches: dict[str, list[dict]] = {}


# ── helpers ────────────────────────────────────────────────────────────────────

def _build_results_keyboard(results: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for i, r in enumerate(results):
        dur = fmt_duration(r["duration"])
        label = f"{i+1}. {r['title'][:40]} [{dur}]"
        buttons.append([InlineKeyboardButton(label, callback_data=f"select:{i}")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)


async def _download_and_enqueue(
    bot: Client,
    chat_id: int,
    user_id: int,
    entry: dict,
    is_video: bool,
    status_msg: Optional[Message] = None,
):
    url = entry["url"]
    try:
        if is_video:
            file_path, info = await download_video(url)
        else:
            file_path, info = await download_audio(url)
    except Exception as e:
        log.exception("Download failed for %s", url)
        text = f"❌ Download failed: {e}"
        if status_msg:
            await status_msg.edit_text(text)
        else:
            await bot.send_message(chat_id, text)
        return

    track = Track(
        title=entry.get("title") or info.get("title", "Unknown"),
        url=url,
        duration=entry.get("duration") or info.get("duration") or 0,
        thumbnail=(
            entry.get("thumbnail")
            or (info.get("thumbnails") or [{}])[-1].get("url", "")
        ),
        requested_by=user_id,
        is_video=is_video,
        file_path=file_path,
    )

    result = await player.play(chat_id, track)
    if result:
        # Track was queued — show queue position message.
        if status_msg:
            await status_msg.edit_text(result)
        else:
            await bot.send_message(chat_id, result)
    else:
        # Playing immediately — player._stream already sends "now playing".
        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass


async def _resolve_and_play(
    bot: Client,
    msg: Message,
    query_or_url: str,
    is_video: bool,
):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    if is_url(query_or_url):
        status = await msg.reply_text("⏳ Fetching info…")
        try:
            info = await get_info(query_or_url)
        except Exception as e:
            await status.edit_text(f"❌ Could not fetch: {e}")
            return

        if info.get("_type") == "playlist" or info.get("entries"):
            try:
                entries = await get_playlist_entries(query_or_url, config.MAX_QUEUE_SIZE)
            except Exception as e:
                await status.edit_text(f"❌ Failed to parse playlist: {e}")
                return

            await status.edit_text(f"📃 Queuing **{len(entries)}** tracks from playlist…")
            for entry in entries:
                await _download_and_enqueue(bot, chat_id, user_id, entry, is_video, None)
            return

        # Single URL
        entry = {
            "title": info.get("title", "Unknown"),
            "url": query_or_url,
            "duration": info.get("duration") or 0,
            "thumbnail": (
                info.get("thumbnail")
                or (info.get("thumbnails") or [{}])[-1].get("url", "")
            ),
        }
        await status.edit_text("⬇️ Downloading…")
        await _download_and_enqueue(bot, chat_id, user_id, entry, is_video, status)
    else:
        # Text query → show top 5 results as inline keyboard.
        status = await msg.reply_text("🔍 Searching YouTube…")
        try:
            results = await search_youtube(query_or_url, max_results=5)
        except Exception as e:
            await status.edit_text(f"❌ Search failed: {e}")
            return

        if not results:
            await status.edit_text("❌ No results found.")
            return

        key = f"{chat_id}:{user_id}"
        _pending_searches[key] = results
        for r in results:
            r["_is_video"] = is_video

        text = "🎵 **Select a track to play:**\n\n"
        for i, r in enumerate(results):
            dur = fmt_duration(r["duration"])
            text += f"`{i+1}.` **{r['title']}** — `{dur}`\n"

        await status.edit_text(text, reply_markup=_build_results_keyboard(results))


# ── Handler registration ───────────────────────────────────────────────────────

def register(bot: Client):

    @bot.on_message(filters.command("play") & filters.group)
    async def cmd_play(client: Client, msg: Message):
        args = msg.text.split(None, 1)
        if len(args) < 2:
            await msg.reply_text("Usage: `/play <song name or YouTube URL>`")
            return

        # Playmode gate
        mode = await get_playmode(msg.chat.id)
        if mode == "admins" and not await is_admin(client, msg.chat.id, msg.from_user.id):
            await msg.reply_text(
                "❌ This group is in **admins-only** play mode.\n"
                "Only admins can start playback. An admin can run `/playmode` to change this."
            )
            return

        await _resolve_and_play(client, msg, args[1].strip(), is_video=False)

    @bot.on_message(filters.command("vplay") & filters.group)
    async def cmd_vplay(client: Client, msg: Message):
        args = msg.text.split(None, 1)
        if len(args) < 2:
            await msg.reply_text("Usage: `/vplay <video name or YouTube URL>`")
            return

        mode = await get_playmode(msg.chat.id)
        if mode == "admins" and not await is_admin(client, msg.chat.id, msg.from_user.id):
            await msg.reply_text(
                "❌ This group is in **admins-only** play mode.\n"
                "Only admins can start playback. An admin can run `/playmode` to change this."
            )
            return

        await _resolve_and_play(client, msg, args[1].strip(), is_video=True)

    # ── Callbacks ──────────────────────────────────────────────────────────────

    @bot.on_callback_query(filters.regex(r"^select:\d+$"))
    async def cb_select(client: Client, query: CallbackQuery):
        idx = int(query.data.split(":")[1])
        key = f"{query.message.chat.id}:{query.from_user.id}"
        results = _pending_searches.pop(key, None)

        if results is None:
            await query.answer("⏰ Session expired. Please search again.", show_alert=True)
            try:
                await query.message.delete()
            except Exception:
                pass
            return

        if idx >= len(results):
            await query.answer("Invalid selection.", show_alert=True)
            return

        chosen = results[idx]
        is_video = chosen.get("_is_video", False)
        await query.answer(f"✅ Selected: {chosen['title'][:30]}")

        status = await query.message.edit_text("⬇️ Downloading…")
        await _download_and_enqueue(
            client,
            query.message.chat.id,
            query.from_user.id,
            chosen,
            is_video,
            status,
        )

    @bot.on_callback_query(filters.regex(r"^cancel$"))
    async def cb_cancel(_, query: CallbackQuery):
        key = f"{query.message.chat.id}:{query.from_user.id}"
        _pending_searches.pop(key, None)
        await query.answer("Cancelled.")
        try:
            await query.message.delete()
        except Exception:
            pass
