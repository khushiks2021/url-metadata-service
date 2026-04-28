import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.metadata import router as metadata_router
from app.services import database


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown: connect to and disconnect from MongoDB."""
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    title="URL Metadata Service",
    description="Collects and serves HTTP headers, cookies, and page source for any URL.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(metadata_router)


@app.get("/health", tags=["health"])
async def health():
    """Basic liveness check."""
    return {"status": "ok"}