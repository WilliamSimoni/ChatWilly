import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from pyrate_limiter import (
    Duration,
    InMemoryBucket,
    Limiter,
    Rate,
    RedisBucket,
)
from redis.asyncio import ConnectionPool as AsyncConnectionPool
from redis.asyncio import Redis as AsyncRedis

from chatwilly_backend.graph.graph import build_agent
from chatwilly_backend.scheduled_jobs.cleanup_old_sessions import cleanup_old_sessions
from chatwilly_backend.settings import global_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def postgres_lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        global_settings.postgres.url
    ) as checkpointer:
        await checkpointer.setup()
        logger.info("Postgres checkpointer initialized.")

        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            cleanup_old_sessions,
            trigger="interval",
            seconds=global_settings.postgres.cleanup_interval_seconds,
            args=[checkpointer, global_settings.postgres.session_ttl_seconds],
            id="cleanup_old_sessions",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Session cleanup scheduler started.")

        app.state.agent = build_agent(checkpointer)
        yield

        scheduler.shutdown()
        logger.info("Session cleanup scheduler stopped.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_rate = [
        Rate(
            global_settings.rate_limit_max_requests,
            global_settings.rate_limit_window_seconds * Duration.SECOND,
        )
    ]

    if global_settings.redis.enabled:
        logger.info(f"Connecting to Redis at {global_settings.redis.url}...")
        try:
            pool = AsyncConnectionPool.from_url(global_settings.redis.url)
            redis_db = AsyncRedis(connection_pool=pool)
            bucket = await RedisBucket.init(
                chat_rate, redis_db, bucket_key="chat_rate_limit"
            )
            logger.info("Redis Rate Limiter initialized.")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}. Falling back to InMemory.")
            bucket = InMemoryBucket(chat_rate)
    else:
        logger.info("Redis disabled. Using In-Memory Rate Limiter.")
        bucket = InMemoryBucket(chat_rate)

    app.state.chat_rate_limiter = Limiter(bucket)

    if global_settings.postgres.enabled:
        async with postgres_lifespan(app):
            yield
    else:
        logger.info("Postgres disabled. Using in-memory checkpointer (no persistence).")
        app.state.agent = build_agent(MemorySaver())
        yield
