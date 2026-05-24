from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = ""
    frontend_dist: Path = Path("/app/frontend-dist")

    bearer_token: str = "dev-token"
    internal_service_token: str = "internal-query-token"
    token_cache_ttl_seconds: int = 60

    groq_api_key: str = ""
    primary_llm_model: str = "llama-3.3-70b-versatile"
    fallback_llm_model: str = "llama-3.1-8b-instant"

    gemini_api_key: str = ""
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768

    default_chunk_max_words: int = 180
    max_context_words: int = 1500
    max_history_turns: int = 5
    run_migrations: bool = True
    seed_demo_data: bool = True

    @property
    def production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()
