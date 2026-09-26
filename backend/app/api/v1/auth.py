"""Authentication router (password and server-side OAuth flows)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError

from app.schemas.responses import ApiResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ProfileResponse,
    OAuthProvidersResponse,
)
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.auth import AuthService
from app.services.oauth import OAuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse[ProfileResponse])
async def register(payload: RegisterRequest, session=Depends(get_db)):
    service = AuthService(session)
    # prevent role escalation by not accepting role in payload
    try:
        user = await service.register(payload.name, payload.email, payload.password)
    except IntegrityError:
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


@router.get("/oauth/{provider}/start")
async def oauth_start(
    provider: str,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Start an authenticated provider-linking flow."""
    return RedirectResponse(OAuthService(session).authorization_url(provider, str(current_user.id)))


@router.post("/oauth/{provider}/start")
async def oauth_link_start(
    provider: str,
    session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ApiResponse(data={"url": OAuthService(session).authorization_url(provider, str(current_user.id))})


@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, session=Depends(get_db)):
    """Start a provider login/registration flow."""
    return RedirectResponse(OAuthService(session).authorization_url(provider))


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    session=Depends(get_db),
):
    if error:
        raise HTTPException(status_code=400, detail=f"{provider.title()} authorization was cancelled")
    if not code or not state:
        raise HTTPException(status_code=400, detail="OAuth callback is missing required parameters")
    return RedirectResponse(await OAuthService(session).callback(provider, code, state))


@router.get("/oauth/providers", response_model=ApiResponse[OAuthProvidersResponse])
async def oauth_providers(current_user=Depends(get_current_user), session=Depends(get_db)):
    providers = await OAuthService(session).providers_for_user(current_user.id)
    return ApiResponse(data=OAuthProvidersResponse(providers=providers))
