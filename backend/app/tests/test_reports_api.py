import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.core.factory import create_app
from app.database.session import get_db


@pytest_asyncio.fixture
async def client():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    app = create_app()

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
    await engine.dispose()


async def authenticated_headers(client: AsyncClient):
    email = f"reports_{uuid.uuid4().hex[:8]}@example.com"
    password = "Secure#2026"
    register = await client.post(
        "/api/v1/auth/register",
        json={"name": "Reports Tester", "email": email, "password": password},
    )
    assert register.status_code == 200
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_reports_require_authentication(client: AsyncClient):
    response = await client.get("/api/v1/reports/infrastructure")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_infrastructure_report_returns_csv_with_real_records(client: AsyncClient):
    headers = await authenticated_headers(client)
    create = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={
            "service_name": "Report API",
            "service_type": "api",
            "host": "report.example",
            "status": "healthy",
        },
    )
    assert create.status_code == 201
    service_id = create.json()["data"]["id"]

    response = await client.get("/api/v1/reports/infrastructure", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "agenttwinops-infrastructure-report-" in response.headers["content-disposition"]
    assert "Report API" in response.text
    assert service_id in response.text


@pytest.mark.asyncio
async def test_incident_report_returns_csv_and_empty_reports_have_headers(client: AsyncClient):
    headers = await authenticated_headers(client)
    infrastructure = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={"service_name": "Incident Report API", "service_type": "api", "host": "localhost"},
    )
    assert infrastructure.status_code == 201
    service_id = infrastructure.json()["data"]["id"]
    incident = await client.post(
        "/api/v1/incidents",
        headers=headers,
        json={"service_id": service_id, "incident_type": "latency", "severity": "high"},
    )
    assert incident.status_code == 201

    response = await client.get("/api/v1/reports/incidents", headers=headers)

    assert response.status_code == 200
    assert "incident_id,service_id,service_name" in response.text
    assert "Incident Report API" in response.text
    assert "latency" in response.text
