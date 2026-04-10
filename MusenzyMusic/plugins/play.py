from pyrogram import filters, types
from MusenzyMusic import app, call_py, db
from MusenzyMusic.utils.ytdl import ytdl
from MusenzyMusic.utils.queue import queue, Track
from MusenzyMusic.utils.thumbnails import thumb_manager
import config
import asyncio

@app.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_handler(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a song name or link.")
    
    query = " ".join(message.command[1:])
    video = message.command[0] == "vplay"
    
    m = await message.reply_text("🔎 Searching...")
    
    track = await ytdl.search(query)
    if not track:
        return await m.edit("Could not find anything.")
    
    track.user = message.from_user.mention
    track.video = video
    
    pos = queue.add(message.chat.id, track)
    
    if pos == 0:
        await m.edit("📥 Downloading...")
        success = await call_py.play(message.chat.id, track)
        if success:
            thumb = await thumb_manager.generate(track)
            await m.delete()
            await message.reply_photo(
                photo=thumb,
                caption=(
                    f"**Now Playing on {config.BOT_NAME}**\n"
                    f"🎵 **Title:** [{track.title}]({track.url})\n"
                    f"⏱️ **Duration:** {track.duration}\n"
                    f"👤 **Requested by:** {track.user}"
                )
            )
        else:
            await m.edit("Failed to play.")
            queue.get_next(message.chat.id) # discard
    else:
        await m.edit(f"✅ Queued at position {pos}")
