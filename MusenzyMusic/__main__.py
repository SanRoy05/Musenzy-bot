import asyncio
import pyrogram.errors

# ──────────────────────────────────────────────────────────────────────────────
# MONKEY-PATCH: Fix compatibility between py-tgcalls 2.2.11 and Pyrogram 2.x
# PyTgCalls expects GroupcallForbidden to exist in pyrogram.errors, but it was 
# removed/renamed in recent Pyrogram versions.
# ──────────────────────────────────────────────────────────────────────────────
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(Exception):
        """Dummy class for py-tgcalls compatibility"""
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pyrogram import idle
from MusenzyMusic.core.instances import app, userbot, call_py
import config

async def init():
    print("🎵 Initializing Musenzy Music Bot...")
    
    # Manually configure plugins BEFORE starting the bot
    # This avoids circular imports during the initial instantiation
    app.plugins = dict(root="MusenzyMusic.plugins")
    
    # Start Clients
    await app.start()
    await userbot.start()
    
    # Start Voice Call Manager
    await call_py.start()
    
    print("🎵 Musenzy Bot is now live!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
