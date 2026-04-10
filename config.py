import os
from dotenv import load_dotenv

load_dotenv()

# API Credentials
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION = os.getenv("SESSION")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Branding
BOT_NAME = "Musenzy"
HELP_HEADER = "🎵 Musenzy Music Bot"
BRANDING_TEXT = "Musenzy Music"

# Limits & Defaults
DURATION_LIMIT = 3600 # 60 minutes
PLAYLIST_LIMIT = 20
DEFAULT_THUMB = "https://telegra.ph/file/edba550d5e1657c96a30c.jpg" # Example fallback

# Paths
DOWNLOAD_DIR = "downloads"
CACHE_DIR = "cache"
DB_PATH = "database.json"
