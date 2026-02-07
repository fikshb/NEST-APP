from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt, JWTError

from app.config import settings
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class MeResponse(BaseModel):
    username: str


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    if data.username != settings.admin_user or data.password != settings.admin_password:
        raise HTTPException(401, "Invalid username or password.")

    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": data.username, "exp": expire}
    token = jwt.encode(payload, settings.api_secret_key, algorithm=JWT_ALGORITHM)

    return LoginResponse(access_token=token, username=data.username)


@router.get("/me", response_model=MeResponse)
def me(username: str = Depends(get_current_user)):
    return MeResponse(username=username)
