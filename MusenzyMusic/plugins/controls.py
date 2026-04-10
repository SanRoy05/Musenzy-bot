from pyrogram import filters, types
from MusenzyMusic.core.instances import app, call_py, db
import config

@app.on_message(filters.command(["pause", "resume", "skip", "stop", "vol", "volume", "loop"]) & filters.group)
async def controls_handler(_, message: types.Message):
    # Permission check: Only sudoers or admins should control the bot
    is_sudo = await db.is_sudo(message.from_user.id)
    if not is_sudo:
        # Check if user is an admin in the group
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [types.enums.ChatMemberStatus.ADMINISTRATOR, types.enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ You don't have permission to use this command.")

    command = message.command[0]
    chat_id = message.chat.id
    
    if command == "pause":
        await call_py.pause(chat_id)
        await message.reply_text("⏸️ **Paused the stream.**")
    
    elif command == "resume":
        await call_py.resume(chat_id)
        await message.reply_text("▶️ **Resumed the stream.**")
        
    elif command == "skip" or command == "next":
        await call_py.play_next(chat_id)
        await message.reply_text("⏭️ **Skipped to the next track.**")
        
    elif command == "stop":
        await call_py.stop(chat_id)
        await message.reply_text("⏹️ **Stopped the stream and cleared the queue.**")

    elif command in ["vol", "volume"]:
        if len(message.command) < 2:
            conf = await db.get_chat_config(chat_id)
            return await message.reply_text(f"🔊 **Current volume:** {conf['volume']}%")
        
        try:
            vol = int(message.command[1])
            if vol < 0 or vol > 200:
                return await message.reply_text("❌ Volume must be between 0 and 200.")
            
            # Note: PyTgCalls doesn't have a direct 'volume' method in some versions but 
            # we can often set it via the stream. For now we update the DB config.
            await db.set_chat_config(chat_id, "volume", vol)
            await message.reply_text(f"🔊 **Volume set to:** {vol}%")
        except:
            await message.reply_text("❌ Invalid volume level.")

    elif command == "loop":
        conf = await db.get_chat_config(chat_id)
        new_loop = not conf.get("loop", False)
        await db.set_chat_config(chat_id, "loop", new_loop)
        await message.reply_text(f"🔁 **Loop is now:** {'Enabled' if new_loop else 'Disabled'}")
