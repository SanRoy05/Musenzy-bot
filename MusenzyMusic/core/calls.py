from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from MusenzyMusic.core.userbot import Userbot
from MusenzyMusic.utils.queue import queue, Track
from MusenzyMusic.utils.ytdl import ytdl
import config
import asyncio

class CallManager:
    def __init__(self, userbot: Userbot):
        self.call_py = PyTgCalls(userbot)
        self._register_handlers()

    def _register_handlers(self):
        @self.call_py.on_stream_end()
        async def on_stream_end(client, update):
            chat_id = update.chat_id
            await self.play_next(chat_id)

    async def start(self):
        await self.call_py.start()

    async def play(self, chat_id: int, track: Track):
        if not track.file_path:
            track.file_path = await ytdl.download(track.url)
        
        if track.file_path:
            stream = MediaStream(track.file_path)
            await self.call_py.play(chat_id, stream)
            return True
        return False

    async def play_next(self, chat_id: int):
        next_track = queue.get_next(chat_id)
        if next_track:
            await self.play(chat_id, next_track)
        else:
            try:
                await self.call_py.leave_call(chat_id)
            except:
                pass

    async def pause(self, chat_id: int):
        await self.call_py.pause_stream(chat_id)

    async def resume(self, chat_id: int):
        await self.call_py.resume_stream(chat_id)

    async def stop(self, chat_id: int):
        queue.clear(chat_id)
        await self.call_py.leave_call(chat_id)
