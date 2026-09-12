from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Platform"
    app_version: str = "0.6.1"
    app_env: str = "dev"
    log_level: str = "INFO"

    auth_mode: Literal["api_key", "oidc"] = "api_key"
    rag_api_key: str = "change-me"
    default_tenant_id: str = "demo"
    oidc_issuer: str = "http://localhost:8080/realms/enterprise-rag"
    oidc_audience: str = "enterprise-rag-api"
    oidc_jwks_url: str = "http://localhost:8080/realms/enterprise-rag/protocol/openid-connect/certs"
    oidc_roles_claim: str = "realm_access.roles"
    oidc_tenant_claim: str = "tenant_id"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "enterprise_rag"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    enable_reranker: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    object_store_enabled: bool = True
    s3_endpoint_url: str = "http://localhost:9000"
    s3_region: str = "us-east-1"
    s3_bucket: str = "enterprise-rag"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minio-change-me"
    s3_secure: bool = False
    object_store_startup_retries: int = 10

    llm_base_url: str = "http://localhost:4000/v1"
    llm_api_key: str = "sk-change-me"
    llm_model: str = "enterprise-rag"
    llm_temperature: float = 0.1

    evaluator_llm_base_url: str | None = None
    evaluator_llm_api_key: str | None = None
    evaluator_llm_model: str | None = None

    agent_enabled: bool = True
    agent_state_enabled: bool = True
    agent_async_jobs_enabled: bool = True
    agent_job_poll_seconds: float = 1.0
    agent_max_steps: int = 10
    agent_max_subqueries: int = 3
    agent_max_tool_calls: int = 6
    agent_approval_ttl_seconds: int = 600
    agent_enable_answer_revision: bool = True
    agent_memory_default_retention_days: int = 7
    agent_memory_max_retention_days: int = 30
    agent_rate_limit_per_minute: int = 30
    agent_budget_max_tokens: int = 12000
    agent_budget_max_cost_usd: float = 0.25
    agent_input_cost_per_1k: float = 0.0
    agent_output_cost_per_1k: float = 0.0

    chunk_size: int = 900
    chunk_overlap: int = 150
    vector_top_k: int = 10
    lexical_top_k: int = 10
    final_top_k: int = 5
    max_upload_mb: int = 20
    max_batch_files: int = 20

    cache_enabled: bool = True
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300

    audit_enabled: bool = True
    postgres_dsn: str = "postgresql://rag:rag-change-me@localhost:5432/rag"

    otel_enabled: bool = True
    otel_service_name: str = "enterprise-rag-api"
    otel_exporter_otlp_traces_endpoint: str | None = None

    operational_feedback_enabled: bool = False
    operational_feedback_path: str = "var/operational-feedback.jsonl"
    operational_feedback_consumer_name: str = "enterprise-rag-platform"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
