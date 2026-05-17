from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "projects"
    api_prefix: str = "/api/v1/projects"
    bearer_token: str = "dev-token"
    identity_service_url: str = ""
    token_cache_ttl_seconds: int = 60


settings = Settings()
