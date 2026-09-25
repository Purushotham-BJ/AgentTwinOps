import pytest

from app.agents.simulation import SimulationAgent
from app.schemas.simulation import SimulationRequest


def test_cpu_scenario_is_deterministic_and_does_not_mutate_baseline():
    agent = SimulationAgent()
    baseline = {"cpu_usage": 20, "memory_usage": 30, "latency_ms": 10, "status": "active"}

    first = agent.simulate(baseline, "cpu_spike", {})
    second = agent.simulate(baseline, "cpu_spike", {})

    assert first == second
    assert first["simulated"]["cpu_usage"] == 65
    assert baseline["cpu_usage"] == 20


@pytest.mark.parametrize(
    ("field", "value"),
    [("cpu_usage", 95), ("memory_usage", 88), ("latency_ms", 750), ("status", "degraded")],
)
def test_custom_changes_are_reflected_in_simulated_state(field, value):
    baseline = {"cpu_usage": 20, "memory_usage": 30, "latency_ms": 10, "status": "active"}
    result = SimulationAgent().simulate(baseline, "custom", {field: value})

    assert result["simulated"][field] == value


def test_request_rejects_invalid_values():
    with pytest.raises(ValueError):
        SimulationRequest(service_id="svc", parameters={"cpu_usage": 101})


def test_noop_scenario_reports_no_change():
    baseline = {"cpu_usage": 20, "memory_usage": 30, "latency_ms": 10, "status": "active"}
    result = SimulationAgent().simulate(baseline, "custom", {})

    assert result["simulated"] == baseline
    assert result["impact_summary"] == ["Scenario does not change the baseline state."]
