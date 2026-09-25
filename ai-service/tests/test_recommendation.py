from app.agents.recommendation import RecommendationAgent


def _state(**overrides):
    service = {"id": "svc-1", "service_name": "orders"}
    metric = {"cpu_usage": 10, "memory_usage": 20, "latency": 20}
    twin = {
        "current_state": {"cpu": 10, "memory": 20, "latency": 20},
        "health_score": 100,
        "failure_probability": 0,
        "operational_status": "HEALTHY",
        "anomalies": [],
    }
    twin.update(overrides)
    return service, metric, twin


def test_healthy_service_has_no_recommendations():
    service, metric, twin = _state()
    assert RecommendationAgent().generate(service, metric, twin, []) == []


def test_rules_are_deterministic_and_sorted():
    service, metric, twin = _state(
        current_state={"cpu": 95, "memory": 92, "latency": 1200},
        health_score=40,
        failure_probability=0.8,
        operational_status="CRITICAL",
        anomalies=[{"type": "HIGH_CPU"}],
    )
    agent = RecommendationAgent()
    first = agent.generate(service, metric, twin, [])
    second = agent.generate(service, metric, twin, [])

    assert first == second
    assert [item["priority"] for item in first][:2] == ["critical", "critical"]
    assert all(item["priority"] in {"critical", "high"} for item in first)
    assert len({item["type"] for item in first}) == len(first)


def test_incident_creates_actionable_recommendation():
    service, metric, twin = _state()
    result = RecommendationAgent().generate(
        service, metric, twin, [{"service_id": "svc-1", "severity": "high"}]
    )

    assert len(result) == 1
    assert result[0]["type"] == "INCIDENT_RESPONSE"
