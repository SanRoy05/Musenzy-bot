import asyncio
from pyrogram import idle
from MusenzyMusic import app, userbot, call_py
import config

async def init():
    print("🎵 Initializing Musenzy Music Bot...")
    
    # 1. Start the bot client (Pyrogram)
    await app.start()
    
    # 2. Start the assistant client (Pyrogram)
    await userbot.start()
    
    # 3. Initialize and start the calls client (PyTgCalls)
    # This must happen AFTER userbot.start() in version 2.2.x
    await call_py.start()
    
    print("🎵 Musenzy Bot is now live!")
    await idle()
    
    # Stop everything on exit
    await app.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
