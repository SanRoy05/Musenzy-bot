"""
permissions.py — 4-level permission system.

Levels (highest → lowest):
    1. OWNER     — user_id == config.OWNER_ID
    2. SUDO      — stored in MongoDB (sudo_users collection)
    3. GROUP ADMIN — Telegram group admin/owner via get_chat_member
    4. AUTH USER — stored per-group in MongoDB (chats.authusers)

Public functions:
    is_owner(user_id) -> bool
    is_admin(client, chat_id, user_id) -> bool     # levels 1+2+3
    is_auth(client, chat_id, user_id) -> bool      # levels 1+2+3+4

Decorators (wrap Pyrogram handlers; auto-reply on denied):
    @owner_only
    @admin_only
    @auth_or_admin
"""
from __future__ import annotations

import logging
from functools import wraps

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, CallbackQuery

import config
from database.db import is_sudo, get_authusers

log = logging.getLogger(__name__)


# ── Core checkers ──────────────────────────────────────────────────────────────

async def is_owner(user_id: int) -> bool:
    """Level 1 — the single bot owner defined by OWNER_ID in config."""
    return user_id == config.OWNER_ID


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """
    Level 1–3 check.
    Returns True if user is: owner OR sudo OR Telegram group admin/owner.
    """
    if await is_owner(user_id):
        return True
    if await is_sudo(user_id):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception as exc:
        log.debug("get_chat_member failed for %s in %s: %s", user_id, chat_id, exc)
        return False


async def is_auth(client: Client, chat_id: int, user_id: int) -> bool:
    """
    Level 1–4 check.
    Returns True if user passes is_admin() OR is in the group's authusers list.
    """
    if await is_admin(client, chat_id, user_id):
        return True
    auth_list = await get_authusers(chat_id)
    return user_id in auth_list


# ── Decorators ─────────────────────────────────────────────────────────────────

def owner_only(func):
    """
    Decorator: restrict handler to the bot owner only (Level 1).
    Works on both Message and CallbackQuery handlers.
    """
    @wraps(func)
    async def wrapper(client: Client, update: Message | CallbackQuery):
        user = getattr(update, "from_user", None)
        if user is None:
            return
        if not await is_owner(user.id):
            deny = "❌ This command is reserved for the **bot owner** only."
            if isinstance(update, CallbackQuery):
                await update.answer(deny, show_alert=True)
            else:
                await update.reply_text(deny)
            return
        return await func(client, update)
    return wrapper


def admin_only(func):
    """
    Decorator: restrict handler to Level 1–3 (owner / sudo / group admin).
    Silently ignores private chats.
    """
    @wraps(func)
    async def wrapper(client: Client, update: Message | CallbackQuery):
        user = getattr(update, "from_user", None)
        if user is None:
            return
        msg = update if isinstance(update, Message) else update.message
        chat_id = msg.chat.id

        if not await is_admin(client, chat_id, user.id):
            deny = "❌ This command is for **group admins** (or sudo users) only."
            if isinstance(update, CallbackQuery):
                await update.answer(deny, show_alert=True)
            else:
                await update.reply_text(deny)
            return
        return await func(client, update)
    return wrapper


def auth_or_admin(func):
    """
    Decorator: allow Level 1–4 (owner / sudo / group admin / auth user).
    Non-group members get denied.
    """
    @wraps(func)
    async def wrapper(client: Client, update: Message | CallbackQuery):
        user = getattr(update, "from_user", None)
        if user is None:
            return
        msg = update if isinstance(update, Message) else update.message
        chat_id = msg.chat.id

        if not await is_auth(client, chat_id, user.id):
            deny = (
                "❌ You need to be a group admin or an **authorized user** "
                "to use this command.\n"
                "Ask an admin to run `/auth` on your account."
            )
            if isinstance(update, CallbackQuery):
                await update.answer(deny, show_alert=True)
            else:
                await update.reply_text(deny)
            return
        return await func(client, update)
    return wrapper
