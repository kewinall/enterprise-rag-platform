from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.agent.approval import (
    consume_approval_request,
    get_approval_request,
    reject_approval_request,
    validate_approval_request,
)
from app.agent.orchestrator import run_agent
from app.agent.tools import execute_tool, list_tool_policies
from app.api.schemas import (
    AgentEvaluationRequest,
    AgentQueryRequest,
    AnswerEvaluationRequest,
    QueryRequest,
    SearchRequest,
)
from app.core.cache import get_cache_store
from app.core.config import get_settings
from app.core.metrics import AGENT_APPROVALS, AGENT_RATE_LIMITED
from app.core.object_store import get_object_store
from app.core.rate_limit import get_agent_rate_limiter
from app.core.security import (
    ROLE_ADMIN,
    ROLE_EDITOR,
    ROLE_VIEWER,
    Principal,
    get_principal,
    looks_like_prompt_injection,
    require_role,
)
from app.evaluation.agent_eval import evaluate_agent_result
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
    await get_cache_store().bump_tenant_revision(principal.tenant_id)

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
    await get_cache_store().bump_tenant_revision(principal.tenant_id)
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


@router.get("/agent/tools")
async def agent_tools(principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    tools = []
    for policy in list_tool_policies():
        tools.append(
            {
                **policy,
                "allowed": principal.has_role(policy["required_role"]),
            }
        )
    return {"tenant_id": principal.tenant_id, "tools": tools}


@router.post("/agent/query")
async def agent_query(request: AgentQueryRequest, principal: PrincipalDep) -> dict:
    require_role(principal, ROLE_VIEWER)
    if looks_like_prompt_injection(request.question):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")
    try:
        rate = await get_agent_rate_limiter().check(
            principal.tenant_id,
            principal.subject,
        )
        if not rate.allowed:
            AGENT_RATE_LIMITED.inc()
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Agent rate limit exceeded",
                    "limit": rate.limit,
                    "retry_after_seconds": rate.retry_after_seconds,
                },
            )
        return await run_agent(
            request.question,
            principal,
            top_k=request.top_k,
            mode=request.mode,
            session_id=request.session_id,
            use_memory=request.use_memory,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/agent/approvals/{action_id}")
async def agent_approval(action_id: str, principal: PrincipalDep) -> dict:
    payload = await get_approval_request(action_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Approval request not found or expired")
    try:
        validate_approval_request(payload, principal)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return payload


@router.post("/agent/approvals/{action_id}/approve")
async def approve_agent_action(action_id: str, principal: PrincipalDep) -> dict:
    try:
        payload = await consume_approval_request(action_id, principal)
        result = await execute_tool(
            principal,
            str(payload["tool_name"]),
            dict(payload.get("arguments") or {}),
            approved=True,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    AGENT_APPROVALS.labels("approved").inc()
    return {
        "status": "approved_and_executed",
        "action_id": action_id,
        "approved_by": principal.subject,
        "result": result,
    }


@router.post("/agent/approvals/{action_id}/reject")
async def reject_agent_action(action_id: str, principal: PrincipalDep) -> dict:
    try:
        result = await reject_approval_request(action_id, principal)
        AGENT_APPROVALS.labels("rejected").inc()
        return result
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/agent/evaluate")
async def evaluate_agent(
    request: AgentEvaluationRequest,
    principal: PrincipalDep,
) -> dict:
    require_role(principal, ROLE_VIEWER)
    evaluation = evaluate_agent_result(
        request.result,
        expected_tools=request.expected_tools,
        expected_status=request.expected_status,
    )
    return {"tenant_id": principal.tenant_id, **evaluation}
