import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl

from app.models.metadata import (
    AcceptedResponse,
    CreatedResponse,
    MetadataRecord,
    MetadataResponse,
    PendingRecord,
    URLRequest,
)
from app.services import collector, database
from app.worker import background


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.post(
    "",
    response_model=CreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Collect and store metadata for a URL",
)
async def create_metadata(body: URLRequest):
    """Fetch headers, cookies, and page source for the given URL
    and store the result in MongoDB."""
    url = str(body.url)

    try:
        data = await collector.fetch_metadata(url)
    except Exception as exc:
        logger.exception("Failed to fetch metadata for %s", url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch URL: {exc}",
        )

    record = MetadataRecord(
        url=url,
        headers=data["headers"],
        cookies=data["cookies"],
        page_source=data["page_source"],
    )

    try:
        await database.upsert_record(record.model_dump())
    except Exception as exc:
        logger.exception("Database write failed for %s", url)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {exc}",
        )

    return CreatedResponse(url=url)


@router.get(
    "",
    response_model=MetadataResponse | AcceptedResponse,
    summary="Retrieve metadata for a URL",
    responses={
        200: {"model": MetadataResponse, "description": "Metadata found."},
        202: {"model": AcceptedResponse, "description": "Collection queued."},
    },
)
async def get_metadata(url: HttpUrl):
    url=str(url)
    """Look up stored metadata for a URL. If the record does not exist,
    return 202 and trigger background collection."""
    try:
        record = await database.find_by_url(url)
    except Exception as exc:
        logger.exception("Database read failed for %s", url)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {exc}",
        )

    if record and record.get("status") == "completed":
        return MetadataResponse(
            url=record["url"],
            headers=record["headers"],
            cookies=record["cookies"],
            page_source=record["page_source"],
            collected_at=record["collected_at"],
        )

    # Cache miss — enqueue background collection and return 202.
    if not background.is_pending(url):
        try:
            pending = PendingRecord(url=url)
            await database.upsert_record(pending.model_dump())
        except Exception:
            logger.exception("Failed to insert pending record for %s", url)

        background.enqueue(url)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=AcceptedResponse(url=url).model_dump(),
    )