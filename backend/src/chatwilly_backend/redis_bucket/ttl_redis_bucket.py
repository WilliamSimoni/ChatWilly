from inspect import isawaitable

from pyrate_limiter import RateItem, RedisBucket


class TTLRedisBucket(RedisBucket):
    def __init__(self, rates, redis, bucket_key, script_hash):
        super().__init__(rates, redis, bucket_key, script_hash)
        self.ttl_seconds = None

    @classmethod
    def init(cls, rates, redis, bucket_key, ttl_seconds: int):
        result = super().init(rates, redis, bucket_key)

        if isawaitable(result):

            async def _async_init():
                bucket = await result
                bucket.ttl_seconds = ttl_seconds
                return bucket

            return _async_init()

        result.ttl_seconds = ttl_seconds
        return result

    def put(self, item: RateItem):
        result = super().put(item)

        if isawaitable(result):

            async def _handle_async():
                success = await result
                await self.redis.expire(self.bucket_key, self.ttl_seconds)
                return success

            return _handle_async()

        self.redis.expire(self.bucket_key, self.ttl_seconds)
        return result
