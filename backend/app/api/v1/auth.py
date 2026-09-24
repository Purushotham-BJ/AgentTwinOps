"""Authentication router (register, login, profile, logout)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.responses import ApiResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ProfileResponse,
)
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse[ProfileResponse])
async def register(payload: RegisterRequest, session=Depends(get_db)):
    service = AuthService(session)
    # prevent role escalation by not accepting role in payload
    try:
        user = await service.register(payload.name, payload.email, payload.password)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    profile = ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
    return ApiResponse(data=profile)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(payload: LoginRequest, session=Depends(get_db)):
    service = AuthService(session)
    token = await service.authenticate(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return ApiResponse(data=TokenResponse(access_token=token))


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(current_user=Depends(get_current_user)):
    # Stateless JWT: instruct client to discard token. No server-side revocation.
    return ApiResponse(data={"message": "Logout successful. Discard the token on client side."})


@router.get("/profile", response_model=ApiResponse[ProfileResponse])
async def profile(current_user=Depends(get_current_user)):
    user = current_user
    profile = ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
    return ApiResponse(data=profile)
