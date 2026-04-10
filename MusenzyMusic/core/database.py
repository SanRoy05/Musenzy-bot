import json
import os
import asyncio
from typing import List, Set

class JsonDatabase:
    def __init__(self, path: str):
        self.path = path
        self.data = {
            "sudoers": [],
            "blacklisted_chats": [],
            "blacklisted_users": [],
            "chats_config": {}
        }
        self.lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    async def get_sudoers(self) -> List[int]:
        async with self.lock:
            return self.data.get("sudoers", [])

    async def add_sudo(self, user_id: int):
        async with self.lock:
            if user_id not in self.data["sudoers"]:
                self.data["sudoers"].append(user_id)
                self._save()

    async def del_sudo(self, user_id: int):
        async with self.lock:
            if user_id in self.data["sudoers"]:
                self.data["sudoers"].remove(user_id)
                self._save()

    async def is_blacklisted(self, chat_id: int) -> bool:
        async with self.lock:
            return chat_id in self.data["blacklisted_chats"] or chat_id in self.data["blacklisted_users"]

    async def blacklist_chat(self, chat_id: int):
        async with self.lock:
            if chat_id not in self.data["blacklisted_chats"]:
                self.data["blacklisted_chats"].append(chat_id)
                self._save()

    async def unblacklist_chat(self, chat_id: int):
        async with self.lock:
            if chat_id in self.data["blacklisted_chats"]:
                self.data["blacklisted_chats"].remove(chat_id)
                self._save()
