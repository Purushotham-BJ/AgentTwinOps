"""Pydantic schemas for authentication endpoints."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime


class OAuthProviderResponse(BaseModel):
    provider: str
    connected: bool
    provider_email: Optional[EmailStr] = None


class OAuthProvidersResponse(BaseModel):
    providers: list[OAuthProviderResponse]
