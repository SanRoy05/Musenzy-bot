from pyrogram import filters, types
from MusenzyMusic import app, call_py, db
import config

@app.on_message(filters.command(["pause", "resume", "skip", "stop"]) & filters.group)
async def controls_handler(_, message: types.Message):
    command = message.command[0]
    
    if command == "pause":
        await call_py.pause(message.chat.id)
        await message.reply_text("⏸️ Paused the stream.")
    
    elif command == "resume":
        await call_py.resume(message.chat.id)
        await message.reply_text("▶️ Resumed the stream.")
        
    elif command == "skip":
        await call_py.play_next(message.chat.id)
        await message.reply_text("⏭️ Skipped the current track.")
        
    elif command == "stop":
        await call_py.stop(message.chat.id)
        await message.reply_text("⏹️ Stopped the stream and cleared the queue.")
