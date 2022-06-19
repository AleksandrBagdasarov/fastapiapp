import aioredis
import json
from conf import ENCODING, REDIS_URL


from typing import Hashable


class MyRedis:

    pool = None
    conn = None

    async def _get_pool(self):
        self.pool = aioredis.ConnectionPool.from_url(
            REDIS_URL,
            decode_responses=True,
            encoding=ENCODING,
        )
        self.conn = aioredis.Redis(connection_pool=self.pool)

    async def set(self, key: str, data: dict, ttl=600) -> None:
        await self._get_pool()
        dumped_data = json.dumps(data)
        self.__check_for_hashable(key)
        await self.conn.set(key, dumped_data, ex=ttl)
        await self.pool.disconnect()

    async def get(self, key: str) -> dict:
        await self._get_pool()
        value = await self.conn.get(key)
        data = {} if not value else json.loads(value)
        await self.pool.disconnect()
        return data

    async def remove(self, key):
        await self._get_pool()
        await self.conn.delete(key)
        await self.pool.disconnect()

    @staticmethod
    def __check_for_hashable(key) -> None:
        if not isinstance(key, Hashable):
            raise TypeError(f"Key {key} is not hashable.")
