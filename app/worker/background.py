import asyncio
import logging
from datetime import datetime, UTC
datetime.now(UTC)

from app.models.metadata import MetadataRecord
from app.services import collector, database


logger = logging.getLogger(__name__)

_pending_tasks: dict[str, asyncio.Task] = {}

# Don't retry failed URLs for at least this many seconds
RETRY_COOLDOWN = 60


async def _collect_and_store(url: str) -> None:
    """Fetch metadata for a URL and persist it to MongoDB."""
    try:
        data = await collector.fetch_metadata(url)

        record = MetadataRecord(
            url=url,
            headers=data["headers"],
            cookies=data["cookies"],
            page_source=data["page_source"],
        )

        await database.upsert_record(record.model_dump())
        logger.info("Background collection completed for %s", url)

    except Exception:
        logger.exception("Background collection failed for %s", url)

        # Mark as failed so we don't retry on every GET
        try:
            await database.upsert_record(
                {
                    "url": url,
                    "status": "failed",
                    "collected_at": datetime.now(UTC),
                }
            )
        except Exception:
            logger.exception("Failed to update record for %s", url)

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