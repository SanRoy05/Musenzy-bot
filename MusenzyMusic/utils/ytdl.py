import asyncio
import yt_dlp
from typing import Optional
from MusenzyMusic.utils.queue import Track
import config

class YouTubeManager:
    def __init__(self):
        self.opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{config.DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        }

    async def search(self, query: str) -> Optional[Track]:
        ydl = yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True})
        def _search():
            return ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        
        try:
            info = await asyncio.to_thread(_search)
            return Track(
                title=info["title"],
                url=info["webpage_url"],
                duration=str(info.get("duration", 0)),
                thumb=info.get("thumbnail", config.DEFAULT_THUMB)
            )
        except Exception:
            return None

    async def download(self, url: str) -> Optional[str]:
        ydl = yt_dlp.YoutubeDL(self.opts)
        def _download():
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
        
        try:
            return await asyncio.to_thread(_download)
        except Exception:
            return None

ytdl = YouTubeManager()
