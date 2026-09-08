from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.schemas import AnswerEvaluationRequest, QueryRequest, SearchRequest
from app.core.config import get_settings
from app.core.security import looks_like_prompt_injection, require_api_key
from app.evaluation.answer_eval import evaluate_answer
from app.ingestion.chunking import create_document_id, split_sections
from app.ingestion.parsers import parse_file
from app.rag.service import answer_question
from app.retrieval.hybrid import hybrid_search
from app.retrieval.store import get_vector_store

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


async def _ingest_upload(
    file: UploadFile,
    document_id: str | None = None,
) -> dict:
    settings = get_settings()
    source = file.filename or "upload"
    suffix = Path(source).suffix.lower()
    payload = await file.read()

    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large: {source}")

    with NamedTemporaryFile(suffix=suffix, delete=True) as temp:
        temp.write(payload)
        temp.flush()
        try:
            sections = parse_file(Path(temp.name))
        except ValueError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc

    resolved_document_id = document_id or create_document_id(source)
    chunks = split_sections(
        sections=sections,
        source=source,
        document_id=resolved_document_id,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )

    store = get_vector_store()
    replaced_chunks = store.delete_document(resolved_document_id)
    store.upsert(chunks)

    return {
        "document_id": resolved_document_id,
        "source": source,
        "chunks": len(chunks),
        "replaced_chunks": replaced_chunks,
        "pages": sorted({chunk.page for chunk in chunks if chunk.page is not None}),
        "sections": sorted({chunk.section for chunk in chunks if chunk.section}),
    }


@router.post("/ingest")
async def ingest(file: Annotated[UploadFile, File()]) -> dict:
    return await _ingest_upload(file)


@router.post("/ingest/batch")
async def ingest_batch(files: Annotated[list[UploadFile], File()]) -> dict:
    settings = get_settings()
    if len(files) > settings.max_batch_files:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files; maximum is {settings.max_batch_files}",
        )
    documents = [await _ingest_upload(file) for file in files]
    return {"count": len(documents), "documents": documents}


@router.get("/documents")
async def list_documents() -> dict:
    documents = get_vector_store().list_document_summaries()
    return {"count": len(documents), "documents": documents}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> dict:
    deleted_chunks = get_vector_store().delete_document(document_id)
    if deleted_chunks == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "deleted_chunks": deleted_chunks}


@router.put("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    file: Annotated[UploadFile, File()],
) -> dict:
    if get_vector_store().count_document(document_id) == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    result = await _ingest_upload(file, document_id=document_id)
    return {"status": "reindexed", **result}


@router.post("/search")
async def search(request: SearchRequest) -> dict:
    filters = request.filters.to_payload() if request.filters else None
    results = hybrid_search(
        request.query,
        final_top_k=request.top_k,
        filters=filters,
        mode=request.mode,
    )
    return {
        "mode": request.mode,
        "filters": filters or {},
        "results": results,
    }


@router.post("/query")
async def query(request: QueryRequest) -> dict:
    if looks_like_prompt_injection(request.question):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")
    filters = request.filters.to_payload() if request.filters else None
    return await answer_question(
        request.question,
        request.top_k,
        filters=filters,
        mode=request.mode,
        use_cache=request.use_cache,
    )


@router.post("/evaluate/answer")
async def evaluate(request: AnswerEvaluationRequest) -> dict:
    return await evaluate_answer(
        question=request.question,
        answer=request.answer,
        contexts=request.contexts,
        reference=request.reference,
    )
