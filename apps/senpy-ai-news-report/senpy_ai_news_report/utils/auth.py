import os
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def _expected_token() -> str:
    token = os.getenv("API_AUTH_TOKEN") or os.getenv("API_BEARER_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing API authentication token. Set API_AUTH_TOKEN (or API_BEARER_TOKEN) env variable."
        )
    return token


async def require_api_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    expected_token = _expected_token()

    if credentials is None or credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsupported authorization scheme",
        )


__all__ = ["require_api_token"]
