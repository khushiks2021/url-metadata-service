import asyncio
import logging
from datetime import datetime

from app.services import collector, database


logger = logging.getLogger(__name__)

_pending_tasks: dict[str, asyncio.Task] = {}


async def _collect_and_store(url: str) -> None:
    """Fetch metadata for a URL and persist it to MongoDB."""
    try:
        data = await collector.fetch_metadata(url)

        record = {
            "url": url,
            "headers": data["headers"],
            "cookies": data["cookies"],
            "page_source": data["page_source"],
            "collected_at": datetime.utcnow(),
            "status": "completed",
        }

        await database.upsert_record(record)
        logger.info("Background collection completed for %s", url)

    except Exception:
        logger.exception("Background collection failed for %s", url)

        try:
            collection = database.get_collection()
            await collection.delete_one({"url": url, "status": "pending"})
        except Exception:
            logger.exception("Failed to clean up pending record for %s", url)

    finally:
        _pending_tasks.pop(url, None)


def enqueue(url: str) -> None:
    """Schedule background metadata collection for a URL.

    If a task for this URL is already running, this is a no-op.
    """
    if url in _pending_tasks:
        logger.debug("Collection already in progress for %s", url)
        return

    task = asyncio.create_task(_collect_and_store(url))
    _pending_tasks[url] = task

    logger.info("Enqueued background collection for %s", url)


def is_pending(url: str) -> bool:
    """Check whether a background task is currently running for the URL."""
    return url in _pending_tasks