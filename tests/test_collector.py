import pytest
import httpx
from pytest_httpx import HTTPXMock

from app.services.collector import fetch_metadata


@pytest.mark.asyncio
class TestFetchMetadata:
    async def test_returns_headers_cookies_source(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://example.com/",
            text="<html><body>hi</body></html>",
            headers={"x-custom": "value", "content-type": "text/html"},
        )

        result = await fetch_metadata("https://example.com/")

        assert result["page_source"] == "<html><body>hi</body></html>"
        assert "x-custom" in result["headers"]
        assert isinstance(result["cookies"], dict)

    async def test_raises_on_server_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://fail.test/",
            status_code=500,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_metadata("https://fail.test/")

    async def test_raises_on_network_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_exception(
            httpx.ConnectError("Connection refused"),
            url="https://down.test/",
        )

        with pytest.raises(httpx.ConnectError):
            await fetch_metadata("https://down.test/")