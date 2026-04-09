"""
handlers/sudo.py — Bot-owner-only sudo user management commands.

All commands guarded by @owner_only (Level 1 — OWNER_ID only).

Commands:
    /addsudo <user_id>  — grant sudo privileges
    /delsudo <user_id>  — revoke sudo privileges
    /sudolist           — list all current sudo users with mentions
"""
from __future__ import annotations

import logging
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

import config
from permissions import owner_only
from database.db import add_sudo, del_sudo, get_sudo_users

log = logging.getLogger(__name__)


async def _resolve_user_id(client: Client, msg: Message) -> Optional[int]:
    """
    Resolve a user_id from:
      1. A replied-to message's sender
      2. A numeric argument
      3. A @username argument
    """
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user.id

    args = msg.text.split(None, 1)
    if len(args) < 2:
        return None

    arg = args[1].strip()
    if arg.lstrip("-").isdigit():
        return int(arg)

    try:
        user = await client.get_users(arg)
        return user.id
    except Exception as e:
        log.debug("Could not resolve user %r: %s", arg, e)
        return None


def register(bot: Client):

    @bot.on_message(filters.command("addsudo"))
    @owner_only
    async def cmd_addsudo(client: Client, msg: Message):
        target_id = await _resolve_user_id(client, msg)
        if target_id is None:
            await msg.reply_text(
                "Usage: `/addsudo <user_id or @username>`\n"
                "Or reply to the user's message with `/addsudo`."
            )
            return

        if target_id == config.OWNER_ID:
            await msg.reply_text("ℹ️ The owner is already the highest authority.")
            return

        await add_sudo(target_id)
        await msg.reply_text(
            f"✅ User `{target_id}` has been added as a **sudo user**.\n"
            f"They now have global admin privileges across all groups."
        )

    @bot.on_message(filters.command("delsudo"))
    @owner_only
    async def cmd_delsudo(client: Client, msg: Message):
        target_id = await _resolve_user_id(client, msg)
        if target_id is None:
            await msg.reply_text(
                "Usage: `/delsudo <user_id or @username>`\n"
                "Or reply to the user's message with `/delsudo`."
            )
            return

        if target_id == config.OWNER_ID:
            await msg.reply_text("❌ Cannot remove the bot owner from sudo.")
            return

        await del_sudo(target_id)
        await msg.reply_text(
            f"✅ User `{target_id}` has been **removed** from sudo users."
        )

    @bot.on_message(filters.command("sudolist"))
    @owner_only
    async def cmd_sudolist(client: Client, msg: Message):
        sudo_ids = await get_sudo_users()
        if not sudo_ids:
            await msg.reply_text("📭 No sudo users configured.")
            return

        lines = [f"🛡 **Sudo Users** ({len(sudo_ids)}):\n"]
        for uid in sudo_ids:
            try:
                user = await client.get_users(uid)
                name = user.first_name or str(uid)
                mention = f"[{name}](tg://user?id={uid})"
                uname = f" @{user.username}" if user.username else ""
            except Exception:
                mention = f"`{uid}`"
                uname = ""
            lines.append(f"• {mention}{uname}")

        await msg.reply_text(
            "\n".join(lines),
            disable_web_page_preview=True,
        )
