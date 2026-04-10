import json
import os
import asyncio
from typing import List, Set
import config

class JsonDatabase:
    def __init__(self, path: str):
        self.path = path
        self.data = {
            "sudoers": [config.OWNER_ID],
            "blacklisted_chats": [],
            "blacklisted_users": [],
            "chats_config": {} # {chat_id: {"volume": 100, "loop": False}}
        }
        self.lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
                    # Force owner to be in sudoers
                    if config.OWNER_ID not in self.data["sudoers"]:
                        self.data["sudoers"].append(config.OWNER_ID)
            except Exception:
                pass

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    async def get_sudoers(self) -> List[int]:
        async with self.lock:
            return self.data.get("sudoers", [])

    async def is_sudo(self, user_id: int) -> bool:
        async with self.lock:
            return user_id in self.data["sudoers"] or user_id == config.OWNER_ID

    async def add_sudo(self, user_id: int):
        async with self.lock:
            if user_id not in self.data["sudoers"]:
                self.data["sudoers"].append(user_id)
                self._save()

    async def del_sudo(self, user_id: int):
        async with self.lock:
            if user_id in self.data["sudoers"] and user_id != config.OWNER_ID:
                self.data["sudoers"].remove(user_id)
                self._save()

    async def is_blacklisted(self, chat_id: int) -> bool:
        async with self.lock:
            return chat_id in self.data["blacklisted_chats"] or chat_id in self.data["blacklisted_users"]

    async def get_chat_config(self, chat_id: int):
        async with self.lock:
            if str(chat_id) not in self.data["chats_config"]:
                self.data["chats_config"][str(chat_id)] = {"volume": 100, "loop": False}
                self._save()
            return self.data["chats_config"][str(chat_id)]

    async def set_chat_config(self, chat_id: int, key: str, value):
        async with self.lock:
            if str(chat_id) not in self.data["chats_config"]:
                self.data["chats_config"][str(chat_id)] = {"volume": 100, "loop": False}
            self.data["chats_config"][str(chat_id)][key] = value
            self._save()
