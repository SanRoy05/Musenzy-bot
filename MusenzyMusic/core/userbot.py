from pyrogram import Client
import config

class Userbot(Client):
    def __init__(self):
        super().__init__(
            name="MusenzyAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SESSION,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        print(f"🎵 Assistant started as @{self.username}")

    async def stop(self):
        await super().stop()
        print(f"🎵 Assistant stopped.")
