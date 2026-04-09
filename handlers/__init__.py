"""
handlers/__init__.py — Aggregates all sub-handler modules.

Usage in bot.py:
    import handlers
    handlers.register(bot)
"""
from __future__ import annotations

from pyrogram import Client

from . import misc, play, controls, settings, sudo


def register(bot: Client) -> None:
    """Register every handler module on the bot client."""
    misc.register(bot)
    play.register(bot)
    controls.register(bot)
    settings.register(bot)
    sudo.register(bot)
