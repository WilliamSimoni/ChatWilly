import logging
from datetime import datetime, timedelta, timezone

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logger = logging.getLogger(__name__)


async def cleanup_old_sessions(checkpointer: AsyncPostgresSaver, ttl: int):
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=ttl)
    seen_threads: set[str] = set()
    expired_threads: list[str] = []

    async for checkpoint_tuple in checkpointer.alist(config=None):
        thread_id = checkpoint_tuple.config["configurable"]["thread_id"]
        if thread_id in seen_threads:
            continue
        seen_threads.add(thread_id)

        ts = datetime.fromisoformat(checkpoint_tuple.checkpoint["ts"])
        if ts < cutoff:
            expired_threads.append(thread_id)

    for thread_id in expired_threads:
        await checkpointer.adelete_thread(thread_id)
        logger.info(f"Cleaned up expired session: {thread_id}")
