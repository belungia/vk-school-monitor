import asyncio
import re
import time
import logging

import aiohttp
from typing import Optional
from datetime import datetime

from src.config import settings
from src.client.scripts import wall_get_script, users_get_script, groups_get_script, groups_get_by_id_script


logger = logging.getLogger(__name__)


class VKCLient:
    def __init__(self):
        self.token = settings.token.token.get_secret_value()
        self.rps = 3
        self.chunk_size = 25

        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(self.rps)
        self._rate_lock = asyncio.Lock()
        self._last_call_time = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def _execute(self, script: str) -> dict:
        async with self._rate_lock:
            now = time.monotonic()

            if self._last_call_time:
                delay = (1 / self.rps) - (now - self._last_call_time)
                if delay > 0:
                    await asyncio.sleep(delay)
            else:
                self._last_call_time = now

            if not self._session:
                raise RuntimeError("Session is not active. Use VKClient as async context manager.")
            
            try:
                async with self._session.get(
                    "https://api.vk.com/method/execute",
                    params={
                        "v": "5.199",
                        "access_token": self.token,
                        "lang": "ru",
                        "code": script,
                    },
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    return data.get("response", "")
                    

            except aiohttp.ClientError as e:
                logger.error(f"HTTP Request failed: {str(e)}")
                raise

    async def wall_get(self, id_last_post_map: dict[int, int | None]):
        if not id_last_post_map:
            return []

        owner_ids = list(id_last_post_map.keys())
        chunks = [owner_ids[i:i+self.chunk_size] for i in range(0, len(owner_ids), self.chunk_size)]
        new_posts = []

        async def _fetch_chunk(ids_chunk: list[int]):
            async with self._semaphore:
                script = wall_get_script(ids_chunk)
                return await self._execute(script)

        chunks_result = await asyncio.gather(*[_fetch_chunk(c) for c in chunks])

        for chunk_result in chunks_result:
            for owner_posts in chunk_result:
                if not owner_posts:
                    continue
                owner_id = owner_posts[0]["owner_id"]
                last_date = id_last_post_map.get(owner_id)

                for post in owner_posts:
                    formatted_post_date = datetime.utcfromtimestamp(post["date"])
                    post_data = {
                        "date": formatted_post_date,
                        "text": post["text"],
                        "link": f"https://vk.com/wall{post['owner_id']}_{post['id']}"
                    }
                    if owner_id < 0:
                        post_data["group_id"] = -owner_id
                        post_data["user_id"] = None
                    else:
                        post_data["user_id"] = owner_id
                        post_data["group_id"] = None

                    if last_date is None or formatted_post_date > last_date:
                        new_posts.append(post_data)
                    else:
                        break

        return new_posts
    
    async def users_get(self, links: list[str]) -> list[dict]:
        if not links:
            return []

        user_ids = []
        for link in links:
            match = re.search(r"vk\.com/(.+)", link)
            if match:
                user_ids.append(match.group(1))

        if not user_ids:
            return []

        script = users_get_script(user_ids)
        users_data_raw = await self._execute(script)

        all_users = []
        if isinstance(users_data_raw, list):
            for user in users_data_raw:
                uid = user.get("id")
                if not uid:
                    continue
                user_data = {
                    "id": uid,
                    "name": user.get("first_name"),
                    "surname": user.get("last_name"),
                    "phone": None,
                    "link": f"https://vk.com/id{uid}",
                    "last_post_date": None,
                }
                all_users.append(user_data)

        return all_users
    
    async def groups_get_by_links(self, links: list[str]) -> list[dict]:
        if not links:
            return []

        group_ids = []
        for link in links:
            match = re.search(r"vk\.com/(.+)", link)
            if match:
                group_ids.append(match.group(1))

        if not group_ids:
            return []

        script = groups_get_by_id_script(group_ids)
        groups_data_raw = await self._execute(script)

        # API.groups.getById в 5.199 отдаёт {"groups": [...]}, в старых версиях — просто список.
        if isinstance(groups_data_raw, dict):
            items = groups_data_raw.get("groups", [])
        elif isinstance(groups_data_raw, list):
            items = groups_data_raw
        else:
            items = []

        all_groups = []
        for group in items:
            gid = group.get("id")
            if not gid:
                continue
            all_groups.append({
                "id": gid,
                "name": group.get("name", ""),
                "link": f"https://vk.com/club{gid}",
                "last_post_date": None,
            })

        return all_groups

    async def groups_get(self, user_ids: list[int]) -> list[dict]:
        if not user_ids:
            return []

        chunks = [user_ids[i:i+self.chunk_size] for i in range(0, len(user_ids), self.chunk_size)]
        all_groups = []

        async def _fetch_chunk(ids_chunk: list[int]):
            async with self._semaphore:
                script = groups_get_script(ids_chunk)
                return await self._execute(script)

        chunks_result = await asyncio.gather(*[_fetch_chunk(c) for c in chunks])

        for chunk_result in chunks_result:
            if not isinstance(chunk_result, list):
                continue
            for groups_response in chunk_result:
                if not groups_response:
                    continue
                items = groups_response.get("items") if isinstance(groups_response, dict) else None
                if not items:
                    continue
                for group in items:
                    gid = group.get("id")
                    if not gid:
                        continue
                    link = f"https://vk.com/club{gid}"
                    group_data = {
                        "id": gid,
                        "name": group.get("name", ""),
                        "link": link
                    }
                    all_groups.append(group_data)

        return all_groups