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


@pytest.mark.asyncio
async def test_prediction_and_simulation_history_are_persisted_and_exported(client: AsyncClient):
    headers = await authenticated_headers(client)
    infrastructure = await client.post(
        "/api/v1/infrastructure",
        headers=headers,
        json={"service_name": "History Report API", "service_type": "api", "host": "localhost"},
    )
    assert infrastructure.status_code == 201
    service_id = infrastructure.json()["data"]["id"]

    prediction = await client.post(
        "/api/v1/predictions/history",
        headers=headers,
        json={
            "service_id": service_id,
            "prediction_type": "failure",
            "predicted_value": 72.5,
            "confidence": 0.88,
            "failure_probability": 0.12,
            "risk_level": "medium",
            "factors": ["CPU trend"],
            "recommended_action": "Monitor closely",
            "status": "SUCCESS",
            "horizon_minutes": 60,
            "historical_metrics": [60.0, 65.0],
            "model_metrics": {"mae": 1.1},
            "prediction_source": "model",
        },
    )
    assert prediction.status_code == 201

    simulation = await client.post(
        "/api/v1/simulations/history",
        headers=headers,
        json={
            "service_id": service_id,
            "scenario": "cpu_spike",
            "status": "completed",
            "baseline_state": {"cpu_usage": 20.0},
            "scenario_changes": {"cpu_usage": 45.0},
            "simulated_state": {"cpu_usage": 65.0},
            "simulated_health_score": 100.0,
            "simulated_failure_probability": 0.0,
            "simulated_operational_status": "HEALTHY",
            "impact_summary": ["CPU usage changed"],
            "predicted_impact": {"cpu_delta": 45.0},
            "recommendations": ["Continue monitoring"],
            "completed_at": "2026-01-01T00:00:00Z",
        },
    )
    assert simulation.status_code == 201

    prediction_history = await client.get("/api/v1/predictions/history", headers=headers)
    simulation_history = await client.get("/api/v1/simulations/history", headers=headers)
    assert prediction_history.status_code == 200
    assert simulation_history.status_code == 200
    assert prediction_history.json()["total"] >= 1
    assert simulation_history.json()["total"] >= 1

    prediction_report = await client.get("/api/v1/reports/predictions", headers=headers)
    simulation_report = await client.get("/api/v1/reports/simulations", headers=headers)
    assert prediction_report.status_code == 200
    assert simulation_report.status_code == 200
    assert "History Report API" in prediction_report.text
    assert "cpu_spike" in simulation_report.text
