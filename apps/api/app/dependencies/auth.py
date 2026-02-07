from fastapi import Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings

JWT_ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.api_secret_key, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Invalid token.")
        return username
    except JWTError:
        raise HTTPException(401, "Invalid or expired token.")


def get_current_user_or_token(
    request: Request,
    token: str | None = Query(None),
) -> str:
    """Auth dependency that checks Bearer header first, then falls back to ?token= query param.
    Used for endpoints that are opened in new browser tabs (preview/download)."""
    jwt_token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        jwt_token = auth_header.split(" ", 1)[1]
    elif token:
        jwt_token = token
    else:
        raise HTTPException(401, "Not authenticated")

    try:
        payload = jwt.decode(jwt_token, settings.api_secret_key, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Invalid token.")
        return username
    except JWTError:
        raise HTTPException(401, "Invalid or expired token.")
