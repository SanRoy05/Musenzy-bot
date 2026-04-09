"""
bot.py — Entry point.

Startup sequence:
    1. Connect to MongoDB
    2. Start userbot client
    3. Start bot client
    4. Start PyTgCalls
    5. Register all handlers
    6. Send startup notification to LOGGER_ID
    7. Run until SIGINT / SIGTERM
"""
from __future__ import annotations

import asyncio
import logging
import signal

# Workaround for Python 3.10+ where get_event_loop() raises if no loop is set
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client
from aiohttp import web

import config
import player
import handlers
from database import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("musenzy")


async def start_web_server() -> None:
    """Launch a background aiohttp server for Koyeb health checks."""
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="OK", status=200))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    log.info("🌐 Health check server running on port %s", config.PORT)


async def main() -> None:
    # ── 1. Database ───────────────────────────────────────────────────────────
    log.info("Initializing JSON database…")
    db.init()

    # ── 2. Web Server (Health Check) ──────────────────────────────────────────
    await start_web_server()

    # ── 3. Userbot (streams audio/video in VC) ────────────────────────────────
    userbot = Client(
        name="musenzy_userbot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.SESSION_STRING,
    )

    # ── 4. Bot (handles commands) ─────────────────────────────────────────────
    bot = Client(
        name="musenzy_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
    )

    # ── 5. PyTgCalls — must be initialised before clients start ───────────────
    call_py = player.init(userbot, bot)

    # ── 6. Register all command / callback handlers ───────────────────────────
    handlers.register(bot)

    log.info("Starting clients…")
    await userbot.start()
    await bot.start()
    await call_py.start()

    # ── 7. Startup notification ───────────────────────────────────────────────
    me = await bot.get_me()
    log.info("✅ Musenzy is live — @%s", me.username)

    # ── 8. Keep running until shutdown signal ─────────────────────────────────
    stop_event = asyncio.Event()

    def _shutdown(*_: object) -> None:
        log.info("Shutdown signal received.")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
        except (NotImplementedError, ValueError):
            # Windows does not support add_signal_handler for all signals.
            signal.signal(sig, _shutdown)

    await stop_event.wait()

    # ── Graceful shutdown ─────────────────────────────────────────────────────
    log.info("Stopping clients…")
    await call_py.stop()
    await bot.stop()
    await userbot.stop()
    log.info("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
