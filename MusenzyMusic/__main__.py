import asyncio
import pyrogram.errors
import importlib
import sys

# ──────────────────────────────────────────────────────────────────────────────
# MONKEY-PATCH: Fix compatibility between py-tgcalls 2.2.11 and Pyrogram 2.x
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
    
    # ──────────────────────────────────────────────────────────────────────────
    # DIAGNOSTIC: Force-import plugins to reveal hidden errors
    # ──────────────────────────────────────────────────────────────────────────
    print("🔍 Diagnosing plugin loading...")
    plugins_to_check = ["start", "play", "controls", "queue"]
    for plugin in plugins_to_check:
        try:
            importlib.import_module(f"MusenzyMusic.plugins.{plugin}")
            print(f"✅ Plugin '{plugin}' imported successfully.")
        except Exception as e:
            print(f"❌ Error loading plugin '{plugin}': {e}")
            import traceback
            traceback.print_exc()
    # ──────────────────────────────────────────────────────────────────────────

    # Manually configure plugins
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
