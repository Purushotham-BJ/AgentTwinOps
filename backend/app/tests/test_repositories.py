"""Integration tests for repository layer using an isolated AsyncSession per test.

Follows the same per-test engine pattern used by `test_models.py` to avoid
event-loop contamination on Windows with asyncpg.
"""
from datetime import datetime
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import select

from app.config.settings import get_settings
from app.models.user import User, UserRole
from app.models.infrastructure import Infrastructure, InfrastructureStatus
from app.models.incident import Incident, IncidentSeverity, ResolutionStatus

from app.repositories.user import UserRepository
from app.repositories.infrastructure import InfrastructureRepository
from app.repositories.incident import IncidentRepository


@pytest_asyncio.fixture(loop_scope="function")
async def db_session():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, echo=False)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio(loop_scope="function")
async def test_user_repository_crud(db_session: AsyncSession):
    repo = UserRepository(db_session)

    email = f"repo_{uuid.uuid4().hex[:8]}@example.com"
    user = User(name="Repo User", email=email, password="hashed", role=UserRole.USER)

    created = await repo.create(user)
    assert created.id is not None

    # commit externally
    await db_session.commit()

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None and fetched.email == email

    fetched_by_email = await repo.get_by_email(email)
    assert fetched_by_email is not None and fetched_by_email.id == created.id

    users = await repo.list()
    assert any(u.id == created.id for u in users)

    # update
    created.name = "Repo User Updated"
    await repo.update(created)
    await db_session.commit()

    updated = await repo.get_by_id(created.id)
    assert updated.name == "Repo User Updated"

    # delete
    await repo.delete(created)
    await db_session.commit()

    deleted = await repo.get_by_id(created.id)
    assert deleted is None


@pytest.mark.asyncio(loop_scope="function")
async def test_infrastructure_repository_and_filters(db_session: AsyncSession):
    infra_repo = InfrastructureRepository(db_session)

    infra = Infrastructure(service_name="svc-a", service_type="api", host="127.0.0.1", status=InfrastructureStatus.ACTIVE)
    created = await infra_repo.create(infra)
    await db_session.commit()

    fetched = await infra_repo.get_by_id(created.id)
    assert fetched is not None and fetched.service_name == "svc-a"

    all_list = await infra_repo.list()
    assert any(i.id == created.id for i in all_list)

    # update
    created.host = "10.1.1.1"
    await infra_repo.update(created)
    await db_session.commit()

    by_status = await infra_repo.list_by_status(InfrastructureStatus.ACTIVE)
    assert any(i.id == created.id for i in by_status)

    by_type = await infra_repo.list_by_type("api")
    assert any(i.id == created.id for i in by_type)

    # delete without incidents should succeed
    await infra_repo.delete(created)
    await db_session.commit()

    assert (await infra_repo.get_by_id(created.id)) is None


@pytest.mark.asyncio(loop_scope="function")
async def test_incident_repository_and_relationships(db_session: AsyncSession):
    infra_repo = InfrastructureRepository(db_session)
    incident_repo = IncidentRepository(db_session)

    # create infrastructure
    infra = Infrastructure(service_name="svc-b", service_type="worker", host="10.2.2.2")
    infra = await infra_repo.create(infra)
    await db_session.commit()

    # create incident
    incident = Incident(service_id=infra.id, severity=IncidentSeverity.HIGH, incident_type="oom", resolution_status=ResolutionStatus.OPEN)
    incident = await incident_repo.create(incident)
    await db_session.commit()

    fetched = await incident_repo.get_by_id(incident.id)
    assert fetched is not None and fetched.service_id == infra.id

    all_inc = await incident_repo.list()
    assert any(i.id == incident.id for i in all_inc)

    by_service = await incident_repo.list_by_service(infra.id)
    assert any(i.id == incident.id for i in by_service)

    by_sev = await incident_repo.list_by_severity(IncidentSeverity.HIGH)
    assert any(i.id == incident.id for i in by_sev)

    by_status = await incident_repo.list_by_resolution_status(ResolutionStatus.OPEN)
    assert any(i.id == incident.id for i in by_status)

    unresolved = await incident_repo.list_unresolved()
    assert any(i.id == incident.id for i in unresolved)

    recent = await incident_repo.list_recent(limit=5)
    assert any(i.id == incident.id for i in recent)

    # update
    incident.resolution_status = ResolutionStatus.RESOLVED
    await incident_repo.update(incident)
    await db_session.commit()

    updated = await incident_repo.get_by_id(incident.id)
    assert updated.resolution_status == ResolutionStatus.RESOLVED

    # confirm cannot delete infrastructure with incident present (RESTRICT)
    # First recreate an infra+incident to test restrict behavior
    infra2 = Infrastructure(service_name="svc-restrict", service_type="db", host="10.9.9.9")
    infra2 = await infra_repo.create(infra2)
    await db_session.commit()

    inc2 = Incident(service_id=infra2.id, incident_type="disk_full")
    inc2 = await incident_repo.create(inc2)
    await db_session.commit()

    # Attempt to delete infra2 should raise IntegrityError on commit
    from sqlalchemy.exc import IntegrityError

    await db_session.delete(infra2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # cleanup: delete incident then infrastructure
    await incident_repo.delete(inc2)
    await db_session.commit()
    await infra_repo.delete(infra2)
    await db_session.commit()
