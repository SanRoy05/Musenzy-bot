from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Track:
    title: str
    url: str
    duration: str
    thumb: str
    file_path: Optional[str] = None
    user: str = "Unknown"
    video: bool = False

class QueueManager:
    def __init__(self):
        self.queues: Dict[int, List[Track]] = {}
        self.loops: Dict[int, bool] = {}

    def add(self, chat_id: int, track: Track) -> int:
        if chat_id not in self.queues:
            self.queues[chat_id] = []
        self.queues[chat_id].append(track)
        return len(self.queues[chat_id]) - 1

    def get_next(self, chat_id: int) -> Optional[Track]:
        if chat_id in self.queues and self.queues[chat_id]:
            # If loop is on, we might handle it differently but let's keep it simple
            # The calls.py will handle loop logic by re-adding or just checking state
            return self.queues[chat_id].pop(0) if self.queues[chat_id] else None
        return None

    def clear(self, chat_id: int):
        self.queues[chat_id] = []

    def get_queue(self, chat_id: int) -> List[Track]:
        return self.queues.get(chat_id, [])

    def is_empty(self, chat_id: int) -> bool:
        return not bool(self.queues.get(chat_id))

queue = QueueManager()
