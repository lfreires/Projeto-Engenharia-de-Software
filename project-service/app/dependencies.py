from functools import lru_cache

from app.repositories.project_repository import InMemoryProjectRepository
from app.services.catalog_service import CatalogService
from app.services.token_validator import TokenValidator


@lru_cache
def get_catalog_service() -> CatalogService:
    return CatalogService(repository=InMemoryProjectRepository())


@lru_cache
def get_token_validator() -> TokenValidator:
    return TokenValidator()
