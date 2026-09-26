import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.core.factory import create_app
from app.core.security import create_access_token, hash_password
from app.database.session import get_db
from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.models.infrastructure import Infrastructure
from app.models.user import User


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


async def create_authenticated_headers(client: AsyncClient):
    email = f"incident_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secure#2026"
    resp = await client.post("/api/v1/auth/register", json={"name": "Incident Tester", "email": email, "password": password})
    assert resp.status_code == 200
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, email


@pytest.mark.asyncio
async def test_incident_auth_crud_and_response_format(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)

    infra_resp = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={"service_name": "API Infra", "service_type": "api", "host": "localhost", "status": "active"},
    )
    assert infra_resp.status_code == 201
    service_id = infra_resp.json()["data"]["id"]

    resp = await client.post(
        "/api/v1/incidents",
        json={
            "service_id": str(service_id),
            "severity": "high",
            "incident_type": "api_latency",
            "resolution_status": "open",
        },
    )
    assert resp.status_code == 401

    resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "service_id": str(service_id),
            "severity": "high",
            "incident_type": "api_latency",
            "resolution_status": "open",
        },
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["success"] is True
    assert "data" in payload
    assert payload["data"]["service_id"] == service_id
    incident_id = payload["data"]["id"]

    resp = await client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["incident_type"] == "api_latency"

    resp = await client.get("/api/v1/incidents", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert any(item["id"] == incident_id for item in items)

    resp = await client.put(
        f"/api/v1/incidents/{incident_id}",
        headers=headers,
        json={"severity": "critical", "resolution_status": "in_progress"},
    )
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["severity"] == "critical"
    assert updated["resolution_status"] == "in_progress"


@pytest.mark.asyncio
async def test_incident_requires_valid_infrastructure_reference(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)
    fake_id = uuid.uuid4()

    resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": str(fake_id), "severity": "low", "incident_type": "missing_service", "resolution_status": "open"},
    )
    assert resp.status_code in (400, 404)


@pytest.mark.asyncio
async def test_incident_invalid_uuid_and_payloads(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)

    resp = await client.get("/api/v1/incidents/not-a-uuid", headers=headers)
    assert resp.status_code == 422

    resp = await client.post("/api/v1/incidents", headers=headers, json={})
    assert resp.status_code == 422

    resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": str(uuid.uuid4()), "severity": "invalid", "incident_type": "bad", "resolution_status": "open"},
    )
    assert resp.status_code == 422

    resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": str(uuid.uuid4()), "severity": "low", "incident_type": "bad", "resolution_status": "invalid"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_incident_not_found_and_update_rejects_missing_record(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)
    fake_id = uuid.uuid4()

    resp = await client.get(f"/api/v1/incidents/{fake_id}", headers=headers)
    assert resp.status_code == 404

    resp = await client.put(f"/api/v1/incidents/{fake_id}", headers=headers, json={"severity": "low"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_incident_delete_restrict_on_infrastructure(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)

    infra_resp = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={"service_name": "Restrict Infra", "service_type": "db", "host": "localhost", "status": "active"},
    )
    assert infra_resp.status_code == 201
    service_id = infra_resp.json()["data"]["id"]

    incident_resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": str(service_id), "severity": "high", "incident_type": "db_fail", "resolution_status": "open"},
    )
    assert incident_resp.status_code == 201

    delete_resp = await client.delete(f"/api/v1/infrastructure/{service_id}", headers=headers)
    assert delete_resp.status_code == 409


@pytest.mark.asyncio
async def test_incident_relationship_to_infrastructure_and_list_includes_service_id(client: AsyncClient):
    headers, _ = await create_authenticated_headers(client)

    infra_resp = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={"service_name": "Linked Infra", "service_type": "cache", "host": "localhost", "status": "healthy"},
    )
    assert infra_resp.status_code == 201
    service_id = infra_resp.json()["data"]["id"]

    incident_resp = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": str(service_id), "severity": "medium", "incident_type": "cache_lag", "resolution_status": "open"},
    )
    assert incident_resp.status_code == 201
    incident_id = incident_resp.json()["data"]["id"]

    resp = await client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
    assert resp.status_code == 200
    payload = resp.json()["data"]
    assert payload["service_id"] == service_id
    assert payload["severity"] == "medium"
    assert payload["incident_type"] == "cache_lag"

    list_resp = await client.get("/api/v1/incidents", headers=headers)
    assert list_resp.status_code == 200
    item = next(i for i in list_resp.json()["data"]["items"] if i["id"] == incident_id)
    assert item["service_id"] == service_id
