import os
import time
import bcrypt
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..db.db import get_pg_pool
from ..db.repositories import employee_repo


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "30"))
REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "1"))


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def device_fingerprint(request: Request) -> str:
    ua = request.headers.get("user-agent", "")
    # prefer X-Forwarded-For when behind proxy
    xff = request.headers.get("x-forwarded-for")
    ip = (xff.split(",")[0].strip() if xff else None) or (request.client.host if request.client else "")
    data = f"{ua}|{ip}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _encode_jwt(payload: dict, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_access_token(*, sub: str, phone: str, fp: str) -> str:
    return _encode_jwt(
        {"sub": sub, "phone": phone, "type": "access", "fp": fp},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN),
    )


def create_refresh_token(*, sub: str, phone: str, fp: str) -> str:
    return _encode_jwt(
        {"sub": sub, "phone": phone, "type": "refresh", "fp": fp},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
    )


auth_scheme = HTTPBearer()


async def get_current_user(request: Request, creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> dict:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid access token")
    # fingerprint check
    fp_claim = payload.get("fp")
    if not fp_claim or fp_claim != device_fingerprint(request):
        raise HTTPException(status_code=401, detail="Token fingerprint mismatch")

    emp_id = int(payload.get("sub"))
    pool = await get_pg_pool()
    user = await employee_repo.get_by_id(pool, emp_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# 路由级依赖：将当前用户放入 request.state.current_user
async def set_current_user(request: Request, creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> None:
    user = await get_current_user(request, creds)
    request.state.current_user = user
