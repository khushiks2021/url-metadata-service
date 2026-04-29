from datetime import datetime, UTC
datetime.now(UTC)
from pydantic import BaseModel, Field, HttpUrl


class URLRequest(BaseModel):
    """Request body for submitting a URL for metadata collection."""
    url: HttpUrl


class MetadataRecord(BaseModel):
    """Full metadata record stored in the database."""
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "completed"


class MetadataResponse(BaseModel):
    """Response returned when metadata is available."""
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime


class AcceptedResponse(BaseModel):
    """Response returned when metadata collection is queued."""
    url: str
    status: str = "accepted"
    message: str = "Metadata collection has been queued. Retry shortly."


class CreatedResponse(BaseModel):
    """Response returned after successful POST."""
    url: str
    status: str = "created"
    message: str = "Metadata collected and stored successfully."


class PendingRecord(BaseModel):
    """A pending placeholder inserted during background collection."""
    url: str
    status: str = "pending"
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))