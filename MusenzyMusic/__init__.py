from MusenzyMusic.core.bot import MusenzyBot
from MusenzyMusic.core.userbot import Userbot
from MusenzyMusic.core.calls import CallManager
from MusenzyMusic.core.database import JsonDatabase
import config

# Global Instances
db = JsonDatabase(config.DB_PATH)
app = MusenzyBot()
userbot = Userbot()
call_py = CallManager(userbot)
