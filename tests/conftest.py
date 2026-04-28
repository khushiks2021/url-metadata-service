import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

from app.services import database


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def mock_db():
    """Replace the real MongoDB connection with an in-memory mock."""
    client = AsyncMongoMockClient()
    db = client["test_url_metadata"]

    database._client = client
    database._db = db

    await db.metadata.create_index("url", unique=True)

    yield db

    await db.metadata.drop()
    database._client = None
    database._db = None