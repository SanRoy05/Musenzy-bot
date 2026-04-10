from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, Update
from pytgcalls.types.stream import StreamAudioEnded
from MusenzyMusic.core.userbot import Userbot
from MusenzyMusic.utils.queue import queue, Track
from MusenzyMusic.utils.ytdl import ytdl
import config
import asyncio

class CallManager:
    def __init__(self, userbot: Userbot):
        self.userbot = userbot
        self.call_py = None

    def _register_handlers(self):
        @self.call_py.on_update()
        async def on_update(client, update: Update):
            if isinstance(update, StreamAudioEnded):
                chat_id = update.chat_id
                await self.play_next(chat_id)

    async def start(self):
        # Initialize only when started to ensure MTProto client is ready
        self.call_py = PyTgCalls(self.userbot.app)
        await self.call_py.start()
        self._register_handlers()

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
