"""Unit and integration tests for SQLAlchemy 2.0 ORM business models.

Each test creates its own dedicated engine with NullPool to avoid
cross-test event-loop contamination (required on Windows with asyncpg).
"""

from datetime import datetime
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.models.incident import Incident, IncidentSeverity, ResolutionStatus
from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.models.user import User, UserRole


@pytest_asyncio.fixture(loop_scope="function")
async def db_session():
    """Per-test isolated AsyncSession using NullPool.

    Creates a fresh engine per test to avoid event-loop cross-contamination
    on Windows (asyncio proactor + asyncpg).
    Rolls back any uncommitted changes on exit via explicit cleanup.
    """
    settings = get_settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


# ---------------------------------------------------------------------------
# User tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="function")
async def test_user_model_crud_and_timestamps(db_session: AsyncSession):
    """Test User creation, fields, enums, and timezone-aware timestamps."""
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Test Engineer",
        email=test_email,
        password="$2b$12$fakehashedpasswordfortesting1234567890",
        role=UserRole.ADMIN,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.name == "Test Engineer"
    assert user.email == test_email
    assert user.role == UserRole.ADMIN
    assert isinstance(user.created_at, datetime)
    assert user.created_at.tzinfo is not None
    assert isinstance(user.updated_at, datetime)
    assert user.updated_at.tzinfo is not None

    # Cleanup
    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio(loop_scope="function")
async def test_user_default_role(db_session: AsyncSession):
    """Test User default role is USER."""
    test_email = f"default_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Default Role User",
        email=test_email,
        password="hash_placeholder",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.role == UserRole.USER

    # Cleanup
    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio(loop_scope="function")
async def test_user_email_unique_constraint(db_session: AsyncSession):
    """Test that duplicate email raises IntegrityError."""
    test_email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    user1 = User(
        name="User One",
        email=test_email,
        password="hash_value_1",
        role=UserRole.USER,
    )
    user2 = User(
        name="User Two",
        email=test_email,
        password="hash_value_2",
        role=UserRole.USER,
    )

    db_session.add(user1)
    await db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    # Cleanup user1
    res = await db_session.execute(select(User).where(User.email == test_email))
    existing = res.scalar_one_or_none()
    if existing:
        await db_session.delete(existing)
        await db_session.commit()


# ---------------------------------------------------------------------------
# Infrastructure tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="function")
async def test_infrastructure_model_crud_and_defaults(db_session: AsyncSession):
    """Test Infrastructure creation, fields, status enum, and timestamps."""
    infra = Infrastructure(
        service_name="api-gateway-service",
        service_type="gateway",
        status=InfrastructureStatus.HEALTHY,
        host="10.0.0.15",
    )

    db_session.add(infra)
    await db_session.commit()
    await db_session.refresh(infra)

    assert isinstance(infra.id, uuid.UUID)
    # service_id is a property alias for id (documentation naming)
    assert infra.service_id == infra.id
    assert infra.service_name == "api-gateway-service"
    assert infra.service_type == "gateway"
    assert infra.status == InfrastructureStatus.HEALTHY
    assert infra.host == "10.0.0.15"
    assert isinstance(infra.created_at, datetime)
    assert infra.created_at.tzinfo is not None
    assert isinstance(infra.updated_at, datetime)

    # Cleanup
    await db_session.delete(infra)
    await db_session.commit()


@pytest.mark.asyncio(loop_scope="function")
async def test_infrastructure_default_status(db_session: AsyncSession):
    """Test Infrastructure default status is ACTIVE."""
    infra = Infrastructure(
        service_name="default-status-svc",
        service_type="api",
        host="10.0.0.99",
    )

    db_session.add(infra)
    await db_session.commit()
    await db_session.refresh(infra)

    assert infra.status == InfrastructureStatus.ACTIVE

    # Cleanup
    await db_session.delete(infra)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Incident tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="function")
async def test_incident_model_foreign_key_and_relationships(db_session: AsyncSession):
    """Test Incident creation, FK constraint, relationships, and RESTRICT delete."""
    # Create parent infrastructure
    infra = Infrastructure(
        service_name="auth-microservice",
        service_type="microservice",
        status=InfrastructureStatus.DEGRADED,
        host="10.0.1.20",
    )
    db_session.add(infra)
    await db_session.commit()
    await db_session.refresh(infra)

    # Create child incident referencing infra
    incident = Incident(
        service_id=infra.id,
        severity=IncidentSeverity.CRITICAL,
        incident_type="high_cpu_exhaustion",
        resolution_status=ResolutionStatus.OPEN,
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)
    await db_session.refresh(infra)  # reload selectin relationship after child commit

    assert isinstance(incident.id, uuid.UUID)
    assert incident.service_id == infra.id
    assert incident.severity == IncidentSeverity.CRITICAL
    assert incident.incident_type == "high_cpu_exhaustion"
    assert incident.resolution_status == ResolutionStatus.OPEN
    assert isinstance(incident.timestamp, datetime)
    assert incident.timestamp.tzinfo is not None

    # Verify bi-directional ORM relationship
    assert incident.infrastructure.service_name == "auth-microservice"
    assert len(infra.incidents) == 1
    assert infra.incidents[0].id == incident.id

    # Test RESTRICT: attempt to delete infra while incident exists → must fail
    # Save IDs as plain Python UUIDs before rollback (ORM state expires after rollback)
    saved_incident_id: uuid.UUID = incident.id
    saved_infra_id: uuid.UUID = infra.id

    await db_session.delete(infra)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # Proper cleanup: remove incident first, then infrastructure (using saved UUIDs)
    res_inc = await db_session.execute(select(Incident).where(Incident.id == saved_incident_id))
    inc_obj = res_inc.scalar_one_or_none()
    if inc_obj:
        await db_session.delete(inc_obj)
        await db_session.commit()

    res_inf = await db_session.execute(select(Infrastructure).where(Infrastructure.id == saved_infra_id))
    inf_obj = res_inf.scalar_one_or_none()
    if inf_obj:
        await db_session.delete(inf_obj)
        await db_session.commit()



@pytest.mark.asyncio(loop_scope="function")
async def test_incident_fk_constraint_fails_for_non_existent_service(db_session: AsyncSession):
    """Test that referencing a non-existent service_id raises IntegrityError."""
    fake_service_id = uuid.uuid4()
    incident = Incident(
        service_id=fake_service_id,
        severity=IncidentSeverity.LOW,
        incident_type="orphan_alert",
        resolution_status=ResolutionStatus.OPEN,
    )

    db_session.add(incident)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio(loop_scope="function")
async def test_incident_default_severity_and_status(db_session: AsyncSession):
    """Test Incident defaults for severity and resolution_status."""
    infra = Infrastructure(
        service_name="defaults-test-svc",
        service_type="worker",
        host="10.0.2.5",
    )
    db_session.add(infra)
    await db_session.commit()
    await db_session.refresh(infra)

    incident = Incident(
        service_id=infra.id,
        incident_type="cpu_spike",
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)

    assert incident.severity == IncidentSeverity.MEDIUM
    assert incident.resolution_status == ResolutionStatus.OPEN

    # Cleanup
    await db_session.delete(incident)
    await db_session.commit()
    await db_session.delete(infra)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Metadata verification
# ---------------------------------------------------------------------------

def test_base_metadata_contains_expected_tables():
    """Verify Base.metadata contains exactly the three intended PostgreSQL tables."""
    from app.database.base import Base
    import app.models  # noqa: F401 — ensure models are imported

    table_names = set(Base.metadata.tables.keys())
    expected = {"users", "infrastructure", "incidents"}

    assert expected.issubset(table_names), (
        f"Missing tables: {expected - table_names}"
    )
    # Verify no unintended tables are present (no digital twin, metrics, etc.)
    unexpected = table_names - expected
    assert not unexpected, (
        f"Unexpected tables found in Base.metadata: {unexpected}"
    )
