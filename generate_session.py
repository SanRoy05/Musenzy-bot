import asyncio
import sys

# Fix for Python 3.12+ where asyncio.get_event_loop() no longer 
# automatically creates a loop, which crashes Pyrogram 2.x during import.
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client

async def generate():
    print("🎵 Musenzy Session Generator (Pyrogram V2)")
    print("──────────────────────────────────────────")
    
    api_id = input("Enter your API_ID: ")
    api_hash = input("Enter your API_HASH: ")
    
    # On Windows, using ":memory:" as a name can sometimes cause 
    # sqlite3.OperationalError. Using in_memory=True is the safer way.
    async with Client("MusenzySession", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
        session_string = await app.export_session_string()
        print("\n✅ Session String Generated Successfully!")
        print("──────────────────────────────────────────")
        print(session_string)
        print("──────────────────────────────────────────")
        print("\nCopy the long string above and paste it into your .env file as SESSION_STRING.")
        print("KEEP THIS SECRET! Anyone with this string can access your account.")

if __name__ == "__main__":
    try:
        asyncio.run(generate())
    except KeyboardInterrupt:
        print("\nStopped.")
