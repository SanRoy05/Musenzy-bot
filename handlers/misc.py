"""
handlers/misc.py — Public commands with no permission gate.

Commands:
    /start  — welcome + command list
    /help   — alias for /start
"""
from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message


def register(bot: Client):

    HELP_TEXT = (
        "👋 **Musenzy Music Bot**\n\n"
        "I stream music and videos directly into Telegram group voice chats.\n\n"

        "**🎵 Playback**\n"
        "/play `<query or URL>` — Play audio (search or URL)\n"
        "/vplay `<query or URL>` — Play video (up to 480p)\n"
        "/queue — Show the current queue\n"
        "/now — Show now-playing info\n\n"

        "**⏯ Controls** _(admin or authorized users)_\n"
        "/pause · /resume · /skip · /stop\n"
        "/vol `<0-200>` — Set volume\n"
        "/loop — Toggle loop mode\n\n"

        "**⚙️ Group Settings** _(group admins)_\n"
        "/playmode — Toggle who can play (admins / everyone)\n"
        "/auth `<user>` — Authorize a user for controls\n"
        "/unauth `<user>` — Revoke authorization\n"
        "/authlist — List authorized users\n\n"

        "**👑 Owner Commands**\n"
        "/addsudo `<user>` — Grant global sudo\n"
        "/delsudo `<user>` — Revoke global sudo\n"
        "/sudolist — List all sudo users\n\n"

        "📌 Tip: For `/play` with a text query, I'll show 5 results. "
        "Just tap one to start playing!"
    )

    @bot.on_message(filters.command(["start", "help"]))
    async def cmd_start(_, msg: Message):
        await msg.reply_text(HELP_TEXT, disable_web_page_preview=True)
