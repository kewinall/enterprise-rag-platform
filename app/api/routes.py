from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.schemas import AnswerEvaluationRequest, QueryRequest, SearchRequest
from app.core.config import get_settings
from app.core.object_store import get_object_store
from app.core.security import (
    ROLE_ADMIN,
    ROLE_EDITOR,
    ROLE_VIEWER,
    Principal,
    get_principal,
    looks_like_prompt_injection,
    require_role,
)
from app.evaluation.answer_eval import evaluate_answer
from app.ingestion.chunking import create_document_id, split_sections
from app.ingestion.parsers import parse_file
from app.rag.service import answer_question
from app.retrieval.hybrid import hybrid_search
from app.retrieval.store import get_vector_store

router = APIRouter(prefix="/api/v1")
PrincipalDep = Annotated[Principal, Depends(get_principal)]


def _scoped_filters(principal: Principal, filters: dict | None = None) -> dict:
    return {**(filters or {}), "tenant_id": principal.tenant_id}


async def _ingest_upload(
    file: UploadFile,
    principal: Principal,
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

    resolved_document_id = document_id or create_document_id(
        source,
        principal.tenant_id,
    )
    object_store = get_object_store()
    object_key: str | None = None

    if settings.object_store_enabled:
        if not object_store.available:
            raise HTTPException(status_code=503, detail="Object store unavailable")
        try:
            object_key = await object_store.put_document(
                tenant_id=principal.tenant_id,
                document_id=resolved_document_id,
                source=source,
                payload=payload,
                content_type=file.content_type,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    chunks = split_sections(
        sections=sections,
        source=source,
        document_id=resolved_document_id,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
        tenant_id=principal.tenant_id,
        object_key=object_key,
    )

    store = get_vector_store()
    replaced_chunks = store.delete_document(
        resolved_document_id,
        principal.tenant_id,
    )
    store.upsert(chunks)

    return {
        "document_id": resolved_document_id,
        "tenant_id": principal.tenant_id,
        "source": source,
        "object_key": object_key,
        "chunks": len(chunks),
        "replaced_chunks": replaced_chunks,
        "pages": sorted({chunk.page for chunk in chunks if chunk.page is not None}),
        "sections": sorted({chunk.section for chunk in chunks if chunk.section}),
    }


@router.get("/me")
async def me(principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    return {
        "subject": principal.subject,
        "tenant_id": principal.tenant_id,
        "roles": sorted(principal.roles),
        "auth_mode": principal.auth_mode,
    }


@router.post("/ingest")
async def ingest(
    file: Annotated[UploadFile, File()],
    principal: PrincipalDep,
) -> dict:
    require_role(principal, ROLE_EDITOR)
    return await _ingest_upload(file, principal)


@router.post("/ingest/batch")
async def ingest_batch(
    files: Annotated[list[UploadFile], File()],
    principal: PrincipalDep,
) -> dict:
    require_role(principal, ROLE_EDITOR)
    settings = get_settings()
    if len(files) > settings.max_batch_files:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files; maximum is {settings.max_batch_files}",
        )
    documents = [await _ingest_upload(file, principal) for file in files]
    return {"count": len(documents), "documents": documents}


@router.get("/documents")
async def list_documents(principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    documents = get_vector_store().list_document_summaries(principal.tenant_id)
    return {"count": len(documents), "documents": documents}


@router.get("/documents/{document_id}/download")
async def download_document(document_id: str, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    store = get_vector_store()
    if store.count_document(document_id, principal.tenant_id) == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    object_key = store.get_document_object_key(document_id, principal.tenant_id)
    if not object_key:
        raise HTTPException(status_code=404, detail="Original object is not available")
    try:
        url = await get_object_store().presigned_download_url(object_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"document_id": document_id, "expires_seconds": 300, "download_url": url}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_ADMIN)
    store = get_vector_store()
    object_key = store.get_document_object_key(document_id, principal.tenant_id)
    if store.count_document(document_id, principal.tenant_id) == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        await get_object_store().delete_object(object_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    deleted_chunks = store.delete_document(document_id, principal.tenant_id)
    return {
        "document_id": document_id,
        "tenant_id": principal.tenant_id,
        "deleted_chunks": deleted_chunks,
    }


@router.put("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    file: Annotated[UploadFile, File()],
    principal: PrincipalDep,
) -> dict:
    require_role(principal, ROLE_EDITOR)
    if get_vector_store().count_document(document_id, principal.tenant_id) == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    result = await _ingest_upload(file, principal, document_id=document_id)
    return {"status": "reindexed", **result}


@router.post("/search")
async def search(request: SearchRequest, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    filters = request.filters.to_payload() if request.filters else None
    scoped_filters = _scoped_filters(principal, filters)
    results = hybrid_search(
        request.query,
        final_top_k=request.top_k,
        filters=scoped_filters,
        mode=request.mode,
    )
    return {
        "mode": request.mode,
        "filters": filters or {},
        "tenant_id": principal.tenant_id,
        "results": results,
    }


@router.post("/query")
async def query(request: QueryRequest, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    if looks_like_prompt_injection(request.question):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")
    filters = request.filters.to_payload() if request.filters else None
    return await answer_question(
        request.question,
        tenant_id=principal.tenant_id,
        top_k=request.top_k,
        filters=filters,
        mode=request.mode,
        use_cache=request.use_cache,
    )


@router.post("/evaluate/answer")
async def evaluate(request: AnswerEvaluationRequest, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    result = await evaluate_answer(
        question=request.question,
        answer=request.answer,
        contexts=request.contexts,
        reference=request.reference,
    )
    return {"tenant_id": principal.tenant_id, **result}
