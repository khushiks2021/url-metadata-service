from datetime import datetime, UTC
from pydantic import BaseModel, Field, HttpUrl


class URLRequest(BaseModel):
    # incoming request body
    url: HttpUrl


class MetadataRecord(BaseModel):
    # stored record in DB
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "completed"


class MetadataResponse(BaseModel):
    # response when data is ready
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    collected_at: datetime


class AcceptedResponse(BaseModel):
    # returned when background job is triggered
    url: str
    status: str = "accepted"
    message: str = "Metadata collection has been queued. Retry shortly."


class CreatedResponse(BaseModel):
    # returned after POST success
    url: str
    status: str = "created"
    message: str = "Metadata collected and stored successfully."


class PendingRecord(BaseModel):
    # temporary entry while processing
    url: str
    status: str = "pending"
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))