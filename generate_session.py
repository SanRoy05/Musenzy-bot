"""
generate_session.py — Standalone script to generate a Pyrogram session string.

Run directly: python generate_session.py
Does NOT require .env — all input is interactive.
"""
import asyncio

# Workaround for Python 3.10+ where get_event_loop() raises if no loop is set
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client


async def main():
    print("=" * 55)
    print("  Musenzy — Userbot Session Generator")
    print("=" * 55)
    print()
    print("You need API_ID and API_HASH from https://my.telegram.org")
    print()

    api_id = int(input("Enter your API_ID: ").strip())
    api_hash = input("Enter your API_HASH: ").strip()

    async with Client(
        name="session_gen",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True,
    ) as app:
        session_string = await app.export_session_string()

    print()
    print("=" * 55)
    print("✅ Session string generated successfully!")
    print()
    print("Copy the string below and set it as SESSION_STRING in your .env:")
    print()
    print(session_string)
    print()
    print("=" * 55)
    print("⚠️  Keep this string SECRET — it gives full account access.")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
