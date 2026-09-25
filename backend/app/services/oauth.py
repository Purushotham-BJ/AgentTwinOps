"""Server-side OAuth identity exchange and account linking."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.security import create_access_token
from app.models.user import User, UserAuthAccount, UserRole

settings = get_settings()


class OAuthService:
    PROVIDERS = {"google", "github"}

    def __init__(self, session: AsyncSession):
        self.session = session

    def _config(self, provider: str) -> tuple[str, str, str]:
        if provider == "google":
            return settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET.get_secret_value(), settings.GOOGLE_REDIRECT_URI
        if provider == "github":
            return settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET.get_secret_value(), settings.GITHUB_REDIRECT_URI
        raise HTTPException(status_code=404, detail="Unsupported OAuth provider")

    def authorization_url(self, provider: str, user_id: str | None = None) -> str:
        client_id, _, redirect_uri = self._config(provider)
        if not client_id:
            raise HTTPException(status_code=503, detail=f"{provider.title()} authentication is not configured")
        state = self._encode_state(provider, user_id)
        if provider == "google":
            params = {"client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code", "scope": "openid email profile", "state": state, "access_type": "online", "prompt": "select_account"}
            return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
        params = {"client_id": client_id, "redirect_uri": redirect_uri, "scope": "read:user user:email", "state": state}
        return "https://github.com/login/oauth/authorize?" + urlencode(params)

    def _encode_state(self, provider: str, user_id: str | None) -> str:
        payload = {"provider": provider, "user_id": user_id, "nonce": secrets.token_urlsafe(16), "exp": int(time.time()) + settings.OAUTH_STATE_TTL_SECONDS}
        raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
        signature = hmac.new(settings.SECRET_KEY.get_secret_value().encode(), raw.encode(), hashlib.sha256).hexdigest()
        return f"{raw}.{signature}"

    def _decode_state(self, state: str, provider: str) -> dict[str, Any]:
        try:
            raw, signature = state.split(".", 1)
            expected = hmac.new(settings.SECRET_KEY.get_secret_value().encode(), raw.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError
            payload = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
            if payload.get("provider") != provider or int(payload.get("exp", 0)) < int(time.time()):
                raise ValueError
            return payload
        except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    async def callback(self, provider: str, code: str, state: str) -> str:
        payload = self._decode_state(state, provider)
        client_id, client_secret, redirect_uri = self._config(provider)
        if not client_id or not client_secret:
            raise HTTPException(status_code=503, detail=f"{provider.title()} authentication is not configured")
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            if provider == "google":
                token_response = await client.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "grant_type": "authorization_code"})
                if token_response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="Unable to complete Google sign-in")
                access_token = token_response.json().get("access_token")
                identity_response = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
                if identity_response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="Unable to validate Google identity")
                profile = identity_response.json()
                if not profile.get("sub") or not profile.get("email") or profile.get("email_verified") is not True:
                    raise HTTPException(status_code=400, detail="Google account email is not verified")
                subject, email, name = str(profile["sub"]), profile["email"].lower(), profile.get("name") or profile["email"].split("@")[0]
            else:
                token_response = await client.post("https://github.com/login/oauth/access_token", data={"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri}, headers={"Accept": "application/json"})
                if token_response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="Unable to complete GitHub sign-in")
                access_token = token_response.json().get("access_token")
                headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
                profile_response = await client.get("https://api.github.com/user", headers=headers)
                emails_response = await client.get("https://api.github.com/user/emails", headers=headers)
                if profile_response.status_code >= 400 or emails_response.status_code >= 400:
                    raise HTTPException(status_code=400, detail="Unable to validate GitHub identity")
                profile, emails = profile_response.json(), emails_response.json()
                verified = next((item for item in emails if item.get("primary") and item.get("verified")), None)
                if not profile.get("id") or not verified:
                    raise HTTPException(status_code=400, detail="GitHub account has no verified primary email")
                subject, email, name = str(profile["id"]), verified["email"].lower(), profile.get("name") or profile.get("login") or email.split("@")[0]
        user = await self._resolve_user(provider, subject, email, name, payload.get("user_id"))
        token = create_access_token(user.id)
        return f"{settings.FRONTEND_URL.rstrip('/')}/oauth/callback#access_token={token}"

    async def _resolve_user(self, provider: str, subject: str, email: str, name: str, link_user_id: str | None) -> User:
        account = (await self.session.execute(select(UserAuthAccount).where(UserAuthAccount.provider == provider, UserAuthAccount.provider_user_id == subject))).scalar_one_or_none()
        if account:
            if link_user_id and str(account.user_id) != link_user_id:
                raise HTTPException(status_code=409, detail="This provider account is already linked to another AgentTwinOps user")
            user = await self.session.get(User, account.user_id)
            if not user:
                raise HTTPException(status_code=409, detail="Linked AgentTwinOps user no longer exists")
            return user
        user = None
        if link_user_id:
            user = await self.session.get(User, link_user_id)
            if not user:
                raise HTTPException(status_code=401, detail="Linking account is no longer available")
        else:
            user = (await self.session.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if not user:
            user = User(name=name, email=email, password=None, role=UserRole.USER)
            self.session.add(user)
            await self.session.flush()
        account = UserAuthAccount(user_id=user.id, provider=provider, provider_user_id=subject, provider_email=email)
        self.session.add(account)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="This provider account is already linked to another AgentTwinOps user")
        return user

    async def providers_for_user(self, user_id) -> list[dict[str, Any]]:
        accounts = (await self.session.execute(select(UserAuthAccount).where(UserAuthAccount.user_id == user_id))).scalars().all()
        by_provider = {account.provider: account for account in accounts}
        return [{"provider": provider, "connected": provider in by_provider, "provider_email": by_provider[provider].provider_email if provider in by_provider else None} for provider in sorted(self.PROVIDERS)]
