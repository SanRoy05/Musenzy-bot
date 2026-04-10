from pyrogram import Client
import config

class MusenzyBot(Client):
    def __init__(self):
        super().__init__(
            name="Musenzy",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="MusenzyMusic/plugins"),
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        print(f"🎵 {config.BOT_NAME} Bot started as @{self.username}")

    async def stop(self):
        await super().stop()
        print(f"🎵 {config.BOT_NAME} Bot stopped.")
