import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.factory import create_app
from app.database.engine import engine
from app.database.session import async_session_factory
from app.models.user import User
from app.security.password_policy import validate_password_strength


VALID_PASSWORDS = ["Agent@123", "Secure#2026", "MyPass!99", "Aa1!aaaa"]
INVALID_PASSWORDS = [
    "password",
    "password123",
    "Password",
    "Password123",
    "12345678",
    "abcdefgh",
    "ABCDEFGH",
    "Abcdefgh",
    "Abcd1234",
    "short@1A",
]


@pytest.mark.parametrize("password", VALID_PASSWORDS)
def test_valid_passwords(password):
    assert validate_password_strength(password) == password


@pytest.mark.parametrize("password", INVALID_PASSWORDS)
def test_invalid_passwords(password):
    with pytest.raises(ValueError):
        validate_password_strength(password)


@pytest.mark.parametrize(
    "password",
    ["Aa1!aaa", "aaaaaaaaA!", "AAAAAAA1!", "aaaaaaaA!", "Aaaaaaaa1"],
)
def test_missing_required_password_condition(password):
    with pytest.raises(ValueError):
        validate_password_strength(password)


def test_password_over_maximum_length_is_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("Aa1!" + "a" * 125)


@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def session():
    async with async_session_factory() as db_session:
        yield db_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_registration_api_rejects_weak_password_without_creating_user(
    client: AsyncClient, session: AsyncSession
):
    for password in INVALID_PASSWORDS + ["Aa1!" + "a" * 125]:
        email = f"weak_{uuid.uuid4().hex}@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={"name": "Weak Password", "email": email, "password": password},
        )
        assert response.status_code == 422
        assert all("input" not in error for error in response.json()["error"]["details"])
        result = await session.execute(select(User).where(User.email == email))
        assert result.scalar_one_or_none() is None

    email = f"exact8_{uuid.uuid4().hex}@example.com"
    response = await client.post(
        "/api/v1/auth/register",
        json={"name": "Exact Eight", "email": email, "password": "Aa1!aaaa"},
    )
    assert response.status_code == 200
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    await session.delete(user)
    await session.commit()
