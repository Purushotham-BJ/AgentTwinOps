from uuid import uuid4

from app.schemas.twin import TwinResponse


def test_twin_response_normalizes_legacy_empty_anomalies_object():
    twin = TwinResponse(
        id=uuid4(),
        service_id=uuid4(),
        last_sync="2026-10-02T10:00:00Z",
        operational_status="UNKNOWN",
        state_version=0,
        trends={},
        anomalies={},
    )

    assert twin.anomalies == []
