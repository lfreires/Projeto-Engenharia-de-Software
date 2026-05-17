from functools import lru_cache

from app.repositories.identity_repository import InMemoryIdentityRepository
from app.services.identity_service import IdentityService


@lru_cache
def get_identity_service() -> IdentityService:
    return IdentityService(repository=InMemoryIdentityRepository())
