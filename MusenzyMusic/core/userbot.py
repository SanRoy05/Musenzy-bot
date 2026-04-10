from pyrogram import Client
import config
import sys

class Userbot(Client):
    def __init__(self):
        if not config.SESSION:
            print("❌ ERROR: SESSION (String Session) is missing in your .env file!")
            print("❌ Assistant cannot start without a valid session string.")
            sys.exit(1)
            
        super().__init__(
            name="MusenzyAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION,
            in_memory=True, # Better for containers, doesn't create a .session file
        )

    async def start(self):
        try:
            await super().start()
            self.id = self.me.id
            self.name = self.me.first_name
            self.username = self.me.username
            print(f"🎵 Assistant started as @{self.username}")
        except Exception as e:
            print(f"❌ Assistant failed to start: {e}")
            print("❌ Ensure your SESSION string is a valid Pyrogram V2 session.")
            sys.exit(1)

    async def stop(self):
        await super().stop()
        print(f"🎵 Assistant stopped.")
