from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Platform"
    app_env: str = "dev"
    log_level: str = "INFO"
    rag_api_key: str = "change-me"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "enterprise_rag"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    enable_reranker: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.2:3b"
    llm_temperature: float = 0.1

    chunk_size: int = 900
    chunk_overlap: int = 150
    vector_top_k: int = 10
    lexical_top_k: int = 10
    final_top_k: int = 5
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
