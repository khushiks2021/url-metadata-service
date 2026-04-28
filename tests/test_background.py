import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.services import database
from app.worker import background


@pytest.mark.asyncio
class TestBackgroundWorker:
    async def test_collect_and_store_persists_record(self):
        fake_data = {
            "headers": {"server": "nginx"},
            "cookies": {"token": "xyz"},
            "page_source": "<p>test</p>",
        }

        with patch(
            "app.worker.background.collector.fetch_metadata",
            new_callable=AsyncMock,
            return_value=fake_data,
        ):
            await background._collect_and_store("https://bg-test.example")

        record = await database.find_by_url("https://bg-test.example")

        assert record is not None
        assert record["status"] == "completed"
        assert record["headers"]["server"] == "nginx"

    async def test_collect_and_store_cleans_up_on_failure(self):
        await database.upsert_record(
            {
                "url": "https://fail-bg.test",
                "status": "pending",
                "collected_at": datetime.utcnow(),
            }
        )

        with patch(
            "app.worker.background.collector.fetch_metadata",
            new_callable=AsyncMock,
            side_effect=Exception("timeout"),
        ):
            await background._collect_and_store("https://fail-bg.test")

        record = await database.find_by_url("https://fail-bg.test")
        assert record is None

    async def test_enqueue_prevents_duplicate_tasks(self):
        background._pending_tasks.clear()

        with patch(
            "app.worker.background.collector.fetch_metadata",
            new_callable=AsyncMock,
            return_value={
                "headers": {},
                "cookies": {},
                "page_source": "",
            },
        ):
            background.enqueue("https://dedup.test")
            background.enqueue("https://dedup.test")

            assert len(
                [k for k in background._pending_tasks if k == "https://dedup.test"]
            ) == 1

            await asyncio.gather(
                *background._pending_tasks.values(),
                return_exceptions=True,
            )

        background._pending_tasks.clear()