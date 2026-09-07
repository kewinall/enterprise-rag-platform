import logging

import httpx
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes import router
from app.core.config import get_settings
from app.retrieval.store import get_vector_store

settings = get_settings()
logging.basicConfig(level=settings.log_level)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(router)
app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    try:
        get_vector_store().client.get_collections()
        return {"status": "ready"}
    except (httpx.HTTPError, ConnectionError, TimeoutError) as exc:
        return {"status": "not-ready", "detail": str(exc)}
