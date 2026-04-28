from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import database
from app.worker import background


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestPostMetadata:
    @patch("app.routes.metadata.collector.fetch_metadata", new_callable=AsyncMock)
    def test_post_creates_record(self, mock_fetch, client):
        mock_fetch.return_value = {
            "headers": {"content-type": "text/html"},
            "cookies": {"session": "abc123"},
            "page_source": "<html></html>",
        }

        resp = client.post("/metadata", json={"url": "https://example.com"})
        assert resp.status_code == 201

        body = resp.json()
        assert body["status"] == "created"
        assert body["url"] == "https://example.com/"

    @patch("app.routes.metadata.collector.fetch_metadata", new_callable=AsyncMock)
    def test_post_returns_502_on_fetch_failure(self, mock_fetch, client):
        mock_fetch.side_effect = Exception("connection refused")

        resp = client.post("/metadata", json={"url": "https://unreachable.test"})
        assert resp.status_code == 502

    def test_post_rejects_invalid_url(self, client):
        resp = client.post("/metadata", json={"url": "not-a-url"})
        assert resp.status_code == 422


class TestGetMetadata:
    @patch("app.routes.metadata.collector.fetch_metadata", new_callable=AsyncMock)
    def test_get_returns_existing_record(self, mock_fetch, client):
        mock_fetch.return_value = {
            "headers": {"content-type": "text/html"},
            "cookies": {},
            "page_source": "<h1>Hello</h1>",
        }

        client.post("/metadata", json={"url": "https://example.com"})

        resp = client.get("/metadata", params={"url": "https://example.com/"})
        assert resp.status_code == 200

        body = resp.json()
        assert body["headers"]["content-type"] == "text/html"
        assert body["page_source"] == "<h1>Hello</h1>"

    def test_get_returns_202_for_missing_record(self, client):
        background._pending_tasks.clear()

        resp = client.get("/metadata", params={"url": "https://new-url.test"})
        assert resp.status_code == 202

        body = resp.json()
        assert body["status"] == "accepted"

        for task in background._pending_tasks.values():
            task.cancel()
        background._pending_tasks.clear()

    def test_get_returns_202_for_pending_record(self, client):
        background._pending_tasks.clear()

        resp1 = client.get("/metadata", params={"url": "https://pending.test"})
        assert resp1.status_code == 202

        resp2 = client.get("/metadata", params={"url": "https://pending.test"})
        assert resp2.status_code == 202

        for task in background._pending_tasks.values():
            task.cancel()
        background._pending_tasks.clear()


class TestHealth:
    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}