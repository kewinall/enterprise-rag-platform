from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalFilter(BaseModel):
    document_id: str | None = Field(default=None, max_length=128)
    source: str | None = Field(default=None, max_length=512)
    content_type: str | None = Field(default=None, max_length=128)
    page: int | None = Field(default=None, ge=1)
    section: str | None = Field(default=None, max_length=512)

    def to_payload(self) -> dict[str, str | int]:
        return self.model_dump(exclude_none=True)


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    mode: Literal["vector", "hybrid"] = "hybrid"
    filters: RetrievalFilter | None = None
    use_cache: bool = True


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: Literal["vector", "hybrid"] = "hybrid"
    filters: RetrievalFilter | None = None


class CitationFeedbackRequest(BaseModel):
    query_id: str = Field(min_length=1, max_length=128)
    document_id: str = Field(min_length=1, max_length=256)
    rank: int = Field(ge=1, le=100)


class TroubleshootingReuseFeedbackRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=256)
    outcome: Literal["success", "partial", "failure"]


class LifecycleFeedbackRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=256)
    reason: Literal[
        "outdated",
        "version_mismatch",
        "broken_source",
        "unclear",
        "missing_step",
        "other",
    ]
    severity: Literal["low", "medium", "high"]


class AnswerEvaluationRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    answer: str = Field(min_length=1, max_length=12000)
    contexts: list[str] = Field(min_length=1, max_length=20)
    reference: str | None = Field(default=None, max_length=12000)


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: Literal["vector", "hybrid"] = "hybrid"
    session_id: UUID | None = None
    use_memory: bool = True


class AgentEvaluationRequest(BaseModel):
    result: dict
    expected_tools: list[str] = Field(default_factory=list, max_length=20)
    expected_status: str | None = Field(default=None, max_length=64)


class AgentSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class AgentMemoryRequest(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    value: str = Field(min_length=1, max_length=4000)
    retention_days: int | None = Field(default=None, ge=1, le=365)


class AgentJobRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: Literal["vector", "hybrid"] = "hybrid"
    session_id: UUID | None = None
    use_memory: bool = True


class MCPRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: str | int | None = None
    method: str = Field(min_length=1, max_length=128)
    params: dict = Field(default_factory=dict)
