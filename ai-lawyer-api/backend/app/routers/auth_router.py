from fastapi import APIRouter, HTTPException, Request, Depends
from ..schemas.auth_schema import RegisterRequest, LoginRequest, TokenPair, MeResponse
from ..schemas.response import ApiResponse
from ..db.db import get_pg_pool
from ..db.repositories import employee_repo
from ..security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    device_fingerprint,
    get_current_user,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse[TokenPair])
async def register(payload: RegisterRequest, request: Request) -> ApiResponse[TokenPair]:
    pool = await get_pg_pool()
    # 唯一性: 手机号不可重复
    existed = await employee_repo.get_by_phone(pool, payload.phone)
    if existed:
        raise HTTPException(status_code=400, detail="手机号已存在！")

    pwd_hash = hash_password(payload.password)
    emp_data = {
        "name": payload.name or payload.phone,
        "phone": payload.phone,
        "password": pwd_hash,
        # token 会在生成 refresh_token 后以哈希形式写入
    }
    new_id = await employee_repo.create(pool, emp_data)

    fp = device_fingerprint(request)
    access = create_access_token(sub=str(new_id), phone=payload.phone, fp=fp)
    refresh = create_refresh_token(sub=str(new_id), phone=payload.phone, fp=fp)

    # 将 refresh token 的哈希存入 employees.token
    await employee_repo.update_token(pool, new_id, hash_password(refresh))

    return ApiResponse(result=TokenPair(access_token=access, refresh_token=refresh))


@router.post("/login", response_model=ApiResponse[TokenPair])
async def login(payload: LoginRequest, request: Request) -> ApiResponse[TokenPair]:
    pool = await get_pg_pool()
    user = await employee_repo.get_by_phone(pool, payload.phone)
    if not user or not user.get("password"):
        raise HTTPException(status_code=401, detail="验证失败")
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="签名失败")

    fp = device_fingerprint(request)
    access = create_access_token(sub=str(user["id"]), phone=user["phone"], fp=fp)
    refresh = create_refresh_token(sub=str(user["id"]), phone=user["phone"], fp=fp)

    await employee_repo.update_token(pool, int(user["id"]), hash_password(refresh))
    return ApiResponse(result=TokenPair(access_token=access, refresh_token=refresh))


@router.post("/refresh", response_model=ApiResponse[TokenPair])
async def refresh_token(request: Request, refresh_token: str) -> ApiResponse[TokenPair]:
    import jwt
    from ..security.auth import JWT_SECRET, JWT_ALGORITHM

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    emp_id = int(payload.get("sub"))
    fp_claim = payload.get("fp")
    fp_now = device_fingerprint(request)
    if not fp_claim or fp_claim != fp_now:
        raise HTTPException(status_code=401, detail="Refresh token fingerprint mismatch")

    pool = await get_pg_pool()
    user = await employee_repo.get_by_id(pool, emp_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 校验 refresh token 与 DB 中哈希
    stored_hash = user.get("token") or ""
    from ..security.auth import verify_password as verify_hash
    if not stored_hash or not verify_hash(refresh_token, stored_hash):
        raise HTTPException(status_code=401, detail="Refresh token not recognized")

    # 颁发新对
    access = create_access_token(sub=str(user["id"]), phone=user["phone"], fp=fp_now)
    new_refresh = create_refresh_token(sub=str(user["id"]), phone=user["phone"], fp=fp_now)
    await employee_repo.update_token(pool, int(user["id"]), hash_password(new_refresh))
    return ApiResponse(result=TokenPair(access_token=access, refresh_token=new_refresh))


@router.get("/me", response_model=ApiResponse[MeResponse])
async def me(current_user: dict = Depends(get_current_user)) -> ApiResponse[MeResponse]:
    return ApiResponse(result=MeResponse(id=current_user["id"], name=current_user.get("name"), phone=current_user.get("phone")))

