from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.schemas import QueryRequest, SearchRequest
from app.core.config import get_settings
from app.core.security import looks_like_prompt_injection, require_api_key
from app.ingestion.chunking import split_text
from app.ingestion.parsers import parse_file
from app.rag.service import answer_question
from app.retrieval.store import get_vector_store

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    payload = await file.read()
    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    with NamedTemporaryFile(suffix=suffix, delete=True) as temp:
        temp.write(payload)
        temp.flush()
        text = parse_file(Path(temp.name))

    chunks = split_text(
        text,
        source=file.filename or "upload",
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    get_vector_store().upsert(chunks)
    return {"source": file.filename, "chunks": len(chunks)}


@router.post("/search")
async def search(request: SearchRequest) -> dict:
    results = get_vector_store().search(request.query, limit=request.top_k)
    return {"results": results}


@router.post("/query")
async def query(request: QueryRequest) -> dict:
    if looks_like_prompt_injection(request.question):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")
    return await answer_question(request.question, request.top_k)
