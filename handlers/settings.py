"""
handlers/settings.py — Per-group settings commands.

All commands guarded by @admin_only (Level 1–3).

Commands:
    /playmode         — toggle between "admins" and "everyone", show current
    /auth             — add a user to this group's authusers
    /unauth           — remove a user from this group's authusers
    /authlist         — list all authorized users in this group
"""
from __future__ import annotations

import logging
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from permissions import admin_only
from database.db import (
    get_playmode,
    set_playmode,
    add_authuser,
    del_authuser,
    get_authusers,
)

log = logging.getLogger(__name__)


# ── Resolve a target user from reply or argument ───────────────────────────────

async def _resolve_target(client: Client, msg: Message) -> Optional[int]:
    """
    Return a user_id from:
      1. A replied-to message's sender
      2. A numeric user_id argument
      3. A @username argument (resolved via Telegram)
    Returns None if nothing found.
    """
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user.id

    args = msg.text.split(None, 1)
    if len(args) < 2:
        return None

    arg = args[1].strip()
    if arg.lstrip("-").isdigit():
        return int(arg)

    # Try to resolve @username
    try:
        user = await client.get_users(arg)
        return user.id
    except Exception as e:
        log.debug("Could not resolve user %r: %s", arg, e)
        return None


# ── Handler registration ───────────────────────────────────────────────────────

def register(bot: Client):

    @bot.on_message(filters.command("playmode") & filters.group)
    @admin_only
    async def cmd_playmode(client: Client, msg: Message):
        chat_id = msg.chat.id
        current = await get_playmode(chat_id)

        # Toggle
        new_mode = "everyone" if current == "admins" else "admins"
        await set_playmode(chat_id, new_mode)

        mode_text = (
            "🌐 **Everyone** — any group member can use /play and /vplay."
            if new_mode == "everyone"
            else "🔒 **Admins only** — only admins, sudo users, and authorized users can play."
        )
        await msg.reply_text(
            f"✅ Play mode changed to **{new_mode}**.\n\n{mode_text}"
        )

    @bot.on_message(filters.command("auth") & filters.group)
    @admin_only
    async def cmd_auth(client: Client, msg: Message):
        target_id = await _resolve_target(client, msg)
        if target_id is None:
            await msg.reply_text(
                "Usage: `/auth <user_id or @username>`\n"
                "Or reply to the user's message with `/auth`."
            )
            return

        await add_authuser(msg.chat.id, target_id)
        await msg.reply_text(
            f"✅ User `{target_id}` has been **authorized** in this group.\n"
            f"They can now use playback control commands."
        )

    @bot.on_message(filters.command("unauth") & filters.group)
    @admin_only
    async def cmd_unauth(client: Client, msg: Message):
        target_id = await _resolve_target(client, msg)
        if target_id is None:
            await msg.reply_text(
                "Usage: `/unauth <user_id or @username>`\n"
                "Or reply to the user's message with `/unauth`."
            )
            return

        await del_authuser(msg.chat.id, target_id)
        await msg.reply_text(
            f"✅ User `{target_id}` has been **unauthorized** in this group."
        )

    @bot.on_message(filters.command("authlist") & filters.group)
    @admin_only
    async def cmd_authlist(client: Client, msg: Message):
        auth_ids = await get_authusers(msg.chat.id)
        if not auth_ids:
            await msg.reply_text("📭 No authorized users in this group.")
            return

        lines = ["👥 **Authorized Users in this group:**\n"]
        for uid in auth_ids:
            try:
                user = await client.get_users(uid)
                name = user.first_name or str(uid)
                mention = f"[{name}](tg://user?id={uid})"
            except Exception:
                mention = f"`{uid}`"
            lines.append(f"• {mention}")

        await msg.reply_text(
            "\n".join(lines),
            disable_web_page_preview=True,
        )
