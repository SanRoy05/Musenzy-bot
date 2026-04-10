import asyncio
from pyrogram import idle
from MusenzyMusic import app, userbot, call_py
import config

async def init():
    print("🎵 Initializing Musenzy Music Bot...")
    
    # Start the bot
    await app.start()
    
    # Start the assistant
    await userbot.start()
    
    # Start the calls client
    await call_py.start()
    
    print("🎵 Musenzy Bot is now live!")
    await idle()
    
    # Stop everything on exit
    await app.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
