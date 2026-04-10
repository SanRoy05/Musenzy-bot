from MusenzyMusic.core.bot import MusenzyBot
from MusenzyMusic.core.userbot import Userbot
from MusenzyMusic.core.calls import CallManager
from MusenzyMusic.core.database import JsonDatabase
import config

# Global Database Instance
db = JsonDatabase(config.DB_PATH)

# Bot Client Instance
app = MusenzyBot()

# Assistant Wrapper Instance
userbot = Userbot()

# Voice Call Manager Instance
# Note: CallManager will access userbot.app (the raw client)
call_py = CallManager(userbot)
