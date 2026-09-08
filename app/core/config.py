from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Platform"
    app_version: str = "0.3.0"
    app_env: str = "dev"
    log_level: str = "INFO"
    rag_api_key: str = "change-me"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "enterprise_rag"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    enable_reranker: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    llm_base_url: str = "http://localhost:4000/v1"
    llm_api_key: str = "sk-change-me"
    llm_model: str = "enterprise-rag"
    llm_temperature: float = 0.1

    evaluator_llm_base_url: str | None = None
    evaluator_llm_api_key: str | None = None
    evaluator_llm_model: str | None = None

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

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
