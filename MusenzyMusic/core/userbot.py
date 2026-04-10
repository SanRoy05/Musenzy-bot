from pyrogram import Client
import config
import sys

class Userbot:
    """
    Assistant Wrapper using Composition instead of Inheritance.
    This ensures py-tgcalls receives a raw pyrogram.Client instance.
    """
    def __init__(self):
        if not config.SESSION:
            print("❌ ERROR: SESSION (String Session) is missing in your .env file!")
            print("❌ Assistant cannot start without a valid session string.")
            sys.exit(1)
            
        self.app = Client(
            name="MusenzyAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION,
            in_memory=True,
        )

    async def start(self):
        try:
            await self.app.start()
            self.id = self.app.me.id
            self.name = self.app.me.first_name
            self.username = self.app.me.username
            print(f"🎵 Assistant started as @{self.username}")
        except Exception as e:
            print(f"❌ Assistant failed to start: {e}")
            print("❌ Ensure your SESSION string is a valid Pyrogram V2 session.")
            sys.exit(1)

    async def stop(self):
        await self.app.stop()
        print(f"🎵 Assistant stopped.")
