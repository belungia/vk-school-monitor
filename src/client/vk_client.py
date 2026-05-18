import asyncio
import time
import logging

import aiohttp
from typing import Optional
from datetime import datetime

from src.config import settings
from src.client.scripts import wall_get_script


logger = logging.getLogger(__name__)


class VKCLient:
    def __init__(self):
        self.token = settings.token.token.get_secret_value()
        self.rps = 3
        
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
        
        CHUNK_SIZE = 25 # limit VK API
        
        ids = list(id_last_post_map.keys())
        chunks = [ids[i:i+CHUNK_SIZE] for i in range(0, len(ids), 25)]
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
                    post_data = {
                        "date": datetime.utcfromtimestamp(post["date"]),
                        "user_id": post["owner_id"],
                        "text": post["text"],
                        "link": f"https://vk.com/wall{post["owner_id"]}_{post["id"]}"
                    }

                    if last_date is None or post["date"] > last_date:
                        new_posts.append(post_data)
                    else:
                        break

        return new_posts
            