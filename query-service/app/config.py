from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = "test-key"
    azure_search_endpoint: str = "https://mock.search.windows.net"
    azure_search_key: str = "test-key"
    azure_search_index: str = "documents"

    primary_llm_model: str = "llama-3.3-70b-versatile"
    fallback_llm_model: str = "llama-3.1-8b-instant"

    top_k: int = 5
    max_context_tokens: int = 2000
    max_history_turns: int = 5

    # Auth — Bearer token simples para integração com módulo de Gerenciamento
    bearer_token: str = "dev-token"


settings = Settings()
