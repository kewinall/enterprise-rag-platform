import logging

import httpx
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes import router
from app.core.config import get_settings
from app.retrieval.store import get_vector_store

settings = get_settings()
logging.basicConfig(level=settings.log_level)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router)
app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}


@app.get("/ready")
async def ready() -> dict:
    try:
        get_vector_store().client.get_collections()
        return {"status": "ready", "version": settings.app_version}
    except (httpx.HTTPError, ConnectionError, TimeoutError) as exc:
        return {"status": "not-ready", "detail": str(exc)}
