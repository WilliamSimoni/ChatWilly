from fastapi import FastAPI
from contextlib import asynccontextmanager
from redis.asyncio import ConnectionPool as AsyncConnectionPool
from redis.asyncio import Redis as AsyncRedis
from pyrate_limiter import (
    InMemoryBucket,
    Rate,
    Duration,
    RedisBucket,
)
from chatwilly_backend.settings import global_settings
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conn = None
    
    
    #set /chat rate limit
    chat_rate_limit = [Rate(global_settings.rate_limit_max_requests, global_settings.rate_limit_window_seconds * Duration.SECOND)]
    bucket_key = "chat_rate_limit"
    if global_settings.redis.enabled:
        logger.info(f"Connecting to Redis at {global_settings.redis.url}...")
        try:
            pool = AsyncConnectionPool.from_url(global_settings.redis.url)
            redis_db = AsyncRedis(connection_pool=pool)
            bucket = await RedisBucket.init(chat_rate_limit, redis_db, bucket_key=bucket_key)
            logger.info("Redis Rate Limiter initialized.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}. Falling back to In-Memory.")
            redis_conn = None
            bucket = InMemoryBucket(chat_rate_limit)
    else:
        logger.info("Redis disabled in settings. Using In-Memory Rate Limiter.")
        bucket = InMemoryBucket(chat_rate_limit)
    
    app.state.chat_rate_limit_bucket = bucket
    
    yield
    
    if redis_conn:
        logger.info("Closing Redis connection...")
        await redis_conn.close()