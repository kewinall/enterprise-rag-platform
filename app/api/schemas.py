from typing import Literal

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


class AnswerEvaluationRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    answer: str = Field(min_length=1, max_length=12000)
    contexts: list[str] = Field(min_length=1, max_length=20)
    reference: str | None = Field(default=None, max_length=12000)


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: Literal["vector", "hybrid"] = "hybrid"


class AgentEvaluationRequest(BaseModel):
    result: dict
    expected_tools: list[str] = Field(default_factory=list, max_length=20)
    expected_status: str | None = Field(default=None, max_length=64)
