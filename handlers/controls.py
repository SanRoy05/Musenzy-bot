"""
handlers/controls.py — Playback control commands.

All commands guarded by @auth_or_admin (Level 1–4).
"""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

import player
import queue_manager as qm
from permissions import auth_or_admin
from ytdl import fmt_duration


def register(bot: Client):

    @bot.on_message(filters.command("pause") & filters.group)
    @auth_or_admin
    async def cmd_pause(client: Client, msg: Message):
        result = await player.pause(msg.chat.id)
        await msg.reply_text(result)

    @bot.on_message(filters.command("resume") & filters.group)
    @auth_or_admin
    async def cmd_resume(client: Client, msg: Message):
        result = await player.resume(msg.chat.id)
        await msg.reply_text(result)

    @bot.on_message(filters.command("skip") & filters.group)
    @auth_or_admin
    async def cmd_skip(client: Client, msg: Message):
        result = await player.skip(msg.chat.id)
        await msg.reply_text(result)

    @bot.on_message(filters.command("stop") & filters.group)
    @auth_or_admin
    async def cmd_stop(client: Client, msg: Message):
        result = await player.stop(msg.chat.id)
        await msg.reply_text(result)

    @bot.on_message(filters.command("vol") & filters.group)
    @auth_or_admin
    async def cmd_vol(client: Client, msg: Message):
        args = msg.text.split(None, 1)
        if len(args) < 2 or not args[1].strip().isdigit():
            await msg.reply_text("Usage: `/vol <0-200>`")
            return
        result = await player.set_volume(msg.chat.id, int(args[1].strip()))
        await msg.reply_text(result)

    @bot.on_message(filters.command("loop") & filters.group)
    @auth_or_admin
    async def cmd_loop(client: Client, msg: Message):
        result = await player.toggle_loop(msg.chat.id)
        await msg.reply_text(result)

    @bot.on_message(filters.command("queue") & filters.group)
    async def cmd_queue(_, msg: Message):
        state = await qm.get_state(msg.chat.id)
        if not state.is_playing and not state.queue:
            await msg.reply_text("📭 Queue is empty.")
            return

        lines = []
        if state.current:
            dur = fmt_duration(state.current.duration)
            loop_icon = " 🔁" if state.loop else ""
            lines.append(f"▶️ **Now:** {state.current.title} `[{dur}]`{loop_icon}")

        for i, t in enumerate(state.queue, 1):
            dur = fmt_duration(t.duration)
            lines.append(f"`{i}.` {t.title} `[{dur}]`")

        await msg.reply_text("\n".join(lines))

    @bot.on_message(filters.command("now") & filters.group)
    async def cmd_now(_, msg: Message):
        state = await qm.get_state(msg.chat.id)
        if not state.current:
            await msg.reply_text("Nothing is playing right now.")
            return
        t = state.current
        dur = fmt_duration(t.duration)
        loop_icon = " 🔁" if state.loop else ""
        await msg.reply_text(
            f"🎵 **Now Playing**{loop_icon}\n"
            f"[{t.title}]({t.url})\n"
            f"⏱ `{dur}` | 🔊 Volume: `{state.volume}`",
            disable_web_page_preview=True,
        )
