import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from prometheus_client import make_asgi_app

from app.api.routes import router
from app.core.audit import get_audit_store
from app.core.cache import get_cache_store
from app.core.config import get_settings
from app.core.telemetry import get_tracer, setup_telemetry
from app.retrieval.store import get_vector_store

settings = get_settings()
logging.basicConfig(level=settings.log_level)
setup_telemetry()
tracer = get_tracer(__name__)

WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    cache = get_cache_store()
    audit = get_audit_store()
    await cache.start()
    await audit.start()
    yield
    await cache.close()
    await audit.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)
app.include_router(router)
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    started = perf_counter()

    with tracer.start_as_current_span("http.request") as span:
        span.set_attribute("http.request.method", request.method)
        span.set_attribute("url.path", request.url.path)
        response = await call_next(request)
        span.set_attribute("http.response.status_code", response.status_code)

    duration_ms = (perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id

    await get_audit_store().record_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        metadata={"user_agent_present": bool(request.headers.get("user-agent"))},
    )
    return response


@app.get("/", include_in_schema=False)
async def web_ui() -> FileResponse:
    return FileResponse(WEB_INDEX)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}


@app.get("/ready")
async def ready() -> dict:
    dependencies = {
        "redis": "ready" if get_cache_store().client is not None else "degraded",
        "postgres": "ready" if get_audit_store().pool is not None else "degraded",
    }
    try:
        get_vector_store().client.get_collections()
        dependencies["qdrant"] = "ready"
        return {
            "status": "ready",
            "version": settings.app_version,
            "dependencies": dependencies,
        }
    except (httpx.HTTPError, ConnectionError, TimeoutError) as exc:
        dependencies["qdrant"] = "not-ready"
        return {
            "status": "not-ready",
            "detail": str(exc),
            "dependencies": dependencies,
        }
