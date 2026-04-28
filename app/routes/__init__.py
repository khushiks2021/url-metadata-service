from fastapi import APIRouter, HTTPException
from ..services import fetch_metadata
from ..models import URLMetadata

metadata_router = APIRouter()

@metadata_router.get("/metadata", response_model=URLMetadata)
async def get_metadata(url: str):
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL")
    return await fetch_metadata(url)
