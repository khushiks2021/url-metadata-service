import logging
import httpx

from app.config import settings


logger = logging.getLogger(__name__)


async def fetch_metadata(url: str) -> dict:
    """Fetch headers, cookies, and page content for a URL."""
    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

        headers = dict(response.headers)
        cookies = dict(response.cookies)
        page_source = response.text

        logger.info(
            "Collected metadata for %s (status %d)",
            url,
            response.status_code,
        )

        return {
            "headers": headers,
            "cookies": cookies,
            "page_source": page_source,
        }