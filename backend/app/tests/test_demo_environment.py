"""Focused tests for deterministic onboarding demo definitions."""

from app.services.demo_environment import (
    DEMO_SEED_KEY,
    DEMO_SERVICES,
    DEMO_VERSION,
    METRIC_COUNT,
    _metric_values,
)


def test_demo_registry_definition_is_shared_and_deterministic():
    assert DEMO_SEED_KEY == "agenttwinops-default-demo"
    assert DEMO_VERSION == "v1"
    assert [service.name for service in DEMO_SERVICES] == [
        "demo-api-gateway",
        "demo-user-service",
        "demo-payment-service",
        "demo-order-service",
        "demo-database-service",
    ]
    assert METRIC_COUNT >= 30


def test_demo_metrics_include_healthy_and_warning_profiles():
    healthy = _metric_values("demo-api-gateway", 29)
    warning = _metric_values("demo-payment-service", 29)
    assert healthy[0] < 70 and healthy[1] < 70 and healthy[4] < 500
    assert warning[0] >= 70 or warning[1] >= 70 or warning[4] >= 500
