import asyncio
from pyrogram import Client

async def generate():
    print("🎵 Musenzy Session Generator (Pyrogram V2)")
    print("──────────────────────────────────────────")
    
    api_id = input("Enter your API_ID: ")
    api_hash = input("Enter your API_HASH: ")
    
    async with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
        session_string = await app.export_session_string()
        print("\n✅ Session String Generated Successfully!")
        print("──────────────────────────────────────────")
        print(session_string)
        print("──────────────────────────────────────────")
        print("\nCopy the long string above and paste it into your .env file as SESSION_STRING.")
        print("KEEP THIS SECRET! Anyone with this string can access your account.")

if __name__ == "__main__":
    asyncio.run(generate())
