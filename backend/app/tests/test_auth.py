"""Integration tests for authentication flows using FastAPI TestClient (Async).

Uses the real application and the project's database. Tests clean up created users.
"""
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.core.factory import create_app
from app.config.settings import get_settings
from app.database.session import async_session_factory
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def session():
    async with async_session_factory() as s:
        yield s


@pytest.mark.asyncio
async def test_register_login_profile_logout(client: AsyncClient, session: AsyncSession):
    email = f"auth_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secure#2026"

    # Register
    resp = await client.post("/api/v1/auth/register", json={"name": "Auth Test", "email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == email
    assert "password" not in data

    # Login
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # Profile
    resp = await client.get("/api/v1/auth/profile", headers=headers)
    assert resp.status_code == 200
    profile = resp.json()["data"]
    assert profile["email"] == email
    assert "password" not in profile

    # Logout
    resp = await client.post("/api/v1/auth/logout", headers=headers)
    assert resp.status_code == 200

    # Cleanup: delete user from DB
    res = await session.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if user:
        await session.delete(user)
        await session.commit()
