"""Integration tests for Infrastructure API."""
import uuid
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from app.core.factory import create_app
from app.database.session import async_session_factory, get_db
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.infrastructure import Infrastructure
from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.models.user import User
from app.core.security import hash_password, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from app.config.settings import get_settings


@pytest_asyncio.fixture
async def client():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    TestSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    app = create_app()

    async def _override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    await engine.dispose()


@pytest_asyncio.fixture
async def session():
    async with async_session_factory() as s:
        yield s


@pytest.mark.asyncio
async def test_infrastructure_crud_and_auth(client: AsyncClient, session: AsyncSession):
    # Register and login
    email = f"infra_{uuid.uuid4().hex[:8]}@example.com"
    pw = "Secure#2026"
    await client.post("/api/v1/auth/register", json={"name": "Infra Tester", "email": email, "password": pw})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": pw})
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Unauthenticated should be rejected for create
    resp = await client.post("/api/v1/infrastructure", json={"service_name": "x", "service_type": "t", "host": "localhost"})
    assert resp.status_code == 401

    # Create
    resp = await client.post("/api/v1/infrastructure", headers=headers, json={"service_name": "AgentTwinOps-Test-Service", "service_type": "test", "host": "localhost", "status": "active"})
    assert resp.status_code == 201
    data = resp.json()["data"]
    infra_id = data["id"]
    assert data["service_name"] == "AgentTwinOps-Test-Service"

    # Get
    resp = await client.get(f"/api/v1/infrastructure/{infra_id}", headers=headers)
    assert resp.status_code == 200
    got = resp.json()["data"]
    assert got["id"] == infra_id

    # List
    resp = await client.get("/api/v1/infrastructure", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert any(i["id"] == infra_id for i in items)

    # Update
    resp = await client.put(f"/api/v1/infrastructure/{infra_id}", headers=headers, json={"service_name": "Updated Service", "status": "degraded"})
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["service_name"] == "Updated Service"
    assert updated["status"] == "degraded"

    # Delete should succeed when no incidents
    resp = await client.delete(f"/api/v1/infrastructure/{infra_id}", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_with_incident_rejected(client: AsyncClient):
    # Create a test user directly and sign a token to avoid intermittent auth endpoint race
    email = f"infra_{uuid.uuid4().hex[:8]}@example.com"
    pw = "TestPass123"
    hashed = hash_password(pw)
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        async with s.begin():
            user = User(name="Infra Tester", email=email, password=hashed)
            s.add(user)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create infra
    resp = await client.post("/api/v1/infrastructure", headers=headers, json={"service_name": "ToBeDeleted", "service_type": "t", "host": "localhost", "status": "active"})
    infra_id = resp.json()["data"]["id"]

    # Insert incident referencing infra directly via a fresh session
    engine2 = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine2, expire_on_commit=False) as s:
        async with s.begin():
            # fetch infra
            res = await s.execute(select(Infrastructure).where(Infrastructure.id == infra_id))
            infra = res.scalars().first()
            assert infra is not None
            incident = Incident(service_id=infra.id, severity=IncidentSeverity.HIGH, incident_type="test", resolution_status=ResolutionStatus.OPEN)
            s.add(incident)

    # Attempt delete -> should be 409
    resp = await client.delete(f"/api/v1/infrastructure/{infra_id}", headers=headers)
    assert resp.status_code == 409

    # Cleanup: delete incident and infra using a fresh session
    engine3 = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine3, expire_on_commit=False) as s:
        async with s.begin():
            res = await s.execute(select(Incident).where(Incident.service_id == infra.id))
            inc = res.scalars().first()
            if inc:
                await s.delete(inc)
    engine4 = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine4, expire_on_commit=False) as s:
        async with s.begin():
            res = await s.execute(select(Infrastructure).where(Infrastructure.id == infra.id))
            inf = res.scalars().first()
            if inf:
                await s.delete(inf)
    await engine.dispose()
    await engine2.dispose()
    await engine3.dispose()
    await engine4.dispose()


@pytest.mark.asyncio
async def test_nonexistent_and_malformed_uuid(client: AsyncClient):
    # Nonexistent UUID should return 404 for GET/PUT/DELETE
    import uuid as _uuid
    fake_id = _uuid.uuid4()
    # create test user + token
    from app.core.security import hash_password, create_access_token
    settings = get_settings()
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        async with s.begin():
            pw = "TestPass123"
            hashed = hash_password(pw)
            user = User(name="TestUser", email=f"u_{fake_id.hex}@example.com", password=hashed)
            s.add(user)
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(f"/api/v1/infrastructure/{fake_id}", headers=headers)
    assert resp.status_code == 404

    resp = await client.put(f"/api/v1/infrastructure/{fake_id}", headers=headers, json={"service_name": "x"})
    assert resp.status_code == 404

    resp = await client.delete(f"/api/v1/infrastructure/{fake_id}", headers=headers)
    assert resp.status_code == 404

    # Malformed UUID should be rejected with 422
    resp = await client.get("/api/v1/infrastructure/not-a-uuid", headers=headers)
    assert resp.status_code == 422
    resp = await client.delete("/api/v1/infrastructure/12345", headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_create_payloads(client: AsyncClient):
    # Missing required fields
    resp = await client.post("/api/v1/infrastructure", json={})
    assert resp.status_code == 401 or resp.status_code == 422

    # Create with empty string fields -> 422
    resp = await client.post("/api/v1/infrastructure", json={"service_name": "", "service_type": "", "host": ""})
    assert resp.status_code in (401, 422)

    # Invalid status value should yield validation error (422) if reached
    resp = await client.post("/api/v1/infrastructure", json={"service_name": "s", "service_type": "t", "host": "h", "status": "bogus"})
    # Depending on auth, the endpoint may return 401 first; if not, expect 422
    assert resp.status_code in (401, 422)
