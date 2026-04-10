from pyrogram import filters, types
from MusenzyMusic import app
from MusenzyMusic.utils.queue import queue
import config

@app.on_message(filters.command(["queue", "now"]) & filters.group)
async def queue_handler(_, message: types.Message):
    chat_id = message.chat.id
    q = queue.get_queue(chat_id)
    
    if not q:
        return await message.reply_text("The queue is empty.")
    
    if message.command[0] == "now":
        track = q[0]
        return await message.reply_text(
            f"**Now Playing on {config.BOT_NAME}:**\n"
            f"🎵 **Title:** {track.title}\n"
            f"👤 **Requested by:** {track.user}"
        )

    text = f"**{config.BOT_NAME} Queue:**\n\n"
    for i, track in enumerate(q):
        text += f"{i+1}. {track.title} (Requested by: {track.user})\n"
    
    await message.reply_text(text)
