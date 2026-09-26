import pytest

from app.agents.recovery import RecoveryAgent
from app.services.orchestration_service import OrchestrationService


@pytest.mark.asyncio
async def test_healthy_recovery_is_empty():
    result = await RecoveryAgent().process({"operational_status": "HEALTHY", "recommendations": []})
    assert result["recovery_recommendations"] == []


@pytest.mark.asyncio
async def test_critical_recovery_is_proposal_only():
    result = await RecoveryAgent().process({
        "operational_status": "CRITICAL",
        "recommendations": [{"action": "Scale compute resources", "priority": "high"}],
    })
    assert result["recovery_recommendations"] == [{
        "action": "Scale compute resources",
        "priority": "high",
        "requires_human_approval": True,
        "execution": "proposal_only",
    }]


def test_operational_routing_is_deterministic():
    service = {"status": "active"}
    twin = {"operational_status": "HEALTHY"}
    metric = {"cpu_usage": 20, "memory_usage": 30, "latency": 10}
    assert OrchestrationService._operational_status(service, twin, metric) == "HEALTHY"
    assert OrchestrationService._operational_status(
        service, twin, {"cpu_usage": 95, "memory_usage": 30, "latency": 10}
    ) == "CRITICAL"
