import time
from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status

from app.config import settings


@dataclass(frozen=True)
class CachedToken:
    token: str
    expires_at: float


class TokenValidator:
    def __init__(self) -> None:
        self._cache: dict[str, CachedToken] = {}

    async def validate(self, token: str, project_id: str | None = None) -> str:
        if self._is_cached(token):
            return token

        if settings.identity_service_url:
            await self._validate_with_identity(token, project_id)
        elif token not in {settings.bearer_token, settings.internal_service_token}:
            self._raise_unauthorized()

        self._cache[token] = CachedToken(
            token=token,
            expires_at=time.monotonic() + settings.token_cache_ttl_seconds,
        )
        return token

    def _is_cached(self, token: str) -> bool:
        cached = self._cache.get(token)
        return cached is not None and cached.expires_at > time.monotonic()

    async def _validate_with_identity(self, token: str, project_id: str | None) -> None:
        url = f"{settings.identity_service_url.rstrip('/')}/api/v1/identity/tokens/validate"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"token": token, "project_id": project_id})

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            self._raise_unauthorized()
        if response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Token is not allowed for this project."},
            )
        response.raise_for_status()

    @staticmethod
    def _raise_unauthorized() -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or missing Bearer token"},
        )
