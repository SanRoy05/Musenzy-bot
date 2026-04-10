from pyrogram import filters, types
from MusenzyMusic import app
import config

@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: types.Message):
    await message.reply_text(
        f"Hi {message.from_user.mention}!\n\nI am **{config.BOT_NAME}**, a fast and powerful music bot.\n\n"
        "Click on the help button to see available commands.",
        reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("Help & Commands", callback_data="help")]
        ])
    )

@app.on_message(filters.command("help"))
async def help_handler(_, message: types.Message):
    await message.reply_text(
        f"**{config.HELP_HEADER}**\n\n"
        "**Available Commands:**\n"
        "• `/play <song>` — Search and play music\n"
        "• `/vplay <song>` — Search and play video\n"
        "• `/pause` — Pause the stream\n"
        "• `/resume` — Resume the stream\n"
        "• `/skip` — Skip current track\n"
        "• `/stop` — Stop and clear queue\n"
        "• `/queue` — Show current queue\n"
    )

@app.on_callback_query(filters.regex("help"))
async def help_callback(_, query: types.CallbackQuery):
    await query.message.edit_text(
        f"**{config.HELP_HEADER}**\n\n"
        "**Available Commands:**\n"
        "• `/play <song>` — Search and play music\n"
        "• `/vplay <song>` — Search and play video\n"
        "• `/pause` — Pause the stream\n"
        "• `/resume` — Resume the stream\n"
        "• `/skip` — Skip current track\n"
        "• `/stop` — Stop and clear queue\n"
        "• `/queue` — Show current queue\n"
    )
