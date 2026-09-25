"""Sprint 6 Fix 3 — focused tests for:

  * InsufficientDataError handling in CPU / memory prediction
  * Successful ML CPU / memory prediction (status == SUCCESS)
  * Twin predicted_state synchronisation (success and failure paths)

All tests are pure unit tests: no live Docker / PostgreSQL / backend required.
Every external dependency is replaced with a lightweight fake or monkeypatch.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.prediction import PredictionAgent
from app.services.model_manager import InsufficientDataError
import app.services.model_manager as model_manager_module


# ─── helpers ─────────────────────────────────────────────────────────────────

def _make_successful_predict(value: float = 55.0):
    """Return a fake predict_* function that mimics a successful ML result."""
    def _predict(service_id, horizon):
        # (predicted_value, model_metrics, feature_matrix, raw_values)
        return (
            value,
            {"mae": 1.2, "rmse": 1.5, "r2": 0.91},
            [[50.0, 51.0, 52.0, 53.0], [51.0, 52.0, 53.0, 54.0]],
            [50.0, 51.0, 52.0, 53.0, 54.0, 55.0],
        )
    return _predict


def _make_insufficient_predict():
    """Return a fake predict_* function that raises InsufficientDataError."""
    def _predict(service_id, horizon):
        raise InsufficientDataError("Only 5 records; need 30")
    return _predict


# ─── Test 1: insufficient CPU history ────────────────────────────────────────

async def test_cpu_insufficient_data_returns_correct_status(monkeypatch):
    """history < MIN_HISTORY → status INSUFFICIENT_DATA, no stochastic fallback."""
    monkeypatch.setattr(model_manager_module, "predict_cpu", _make_insufficient_predict())

    agent = PredictionAgent()
    result = await agent._predict_cpu("svc-test", 60)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["predicted_value"] == 0.0
    assert result["failure_probability"] == 0.0
    assert result["recommended_action"] == "Insufficient historical data for a reliable prediction"
    assert result["prediction_source"] == "none"
    assert result["historical_metrics"] == []
    assert result["feature_vector"] == []


async def test_cpu_insufficient_data_does_not_call_stochastic_fallback(monkeypatch):
    """Stochastic fallback path must NOT be invoked when InsufficientDataError fires."""
    import random as random_module

    monkeypatch.setattr(model_manager_module, "predict_cpu", _make_insufficient_predict())

    random_calls = []
    original_random = random_module.random

    def tracking_random():
        random_calls.append(1)
        return original_random()

    # Patch random.random inside the prediction agent module
    with patch("app.agents.prediction.random.random", side_effect=tracking_random):
        agent = PredictionAgent()
        result = await agent._predict_cpu("svc-test", 60)

    assert result["status"] == "INSUFFICIENT_DATA"
    # random() must not have been called (no stochastic fallback)
    assert len(random_calls) == 0, (
        f"random.random() was called {len(random_calls)} times — "
        "stochastic fallback must not fire on InsufficientDataError"
    )


# ─── Test 2: insufficient memory history ─────────────────────────────────────

async def test_memory_insufficient_data_returns_correct_status(monkeypatch):
    """history < MIN_HISTORY (memory) → status INSUFFICIENT_DATA."""
    monkeypatch.setattr(model_manager_module, "predict_memory", _make_insufficient_predict())

    agent = PredictionAgent()
    result = await agent._predict_memory("svc-test", 60)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["predicted_value"] == 0.0
    assert result["failure_probability"] == 0.0
    assert result["recommended_action"] == "Insufficient historical data for a reliable prediction"
    assert result["prediction_source"] == "none"
    assert result["historical_metrics"] == []
    assert result["feature_vector"] == []


async def test_memory_insufficient_data_does_not_call_stochastic_fallback(monkeypatch):
    """Stochastic fallback must NOT fire for memory INSUFFICIENT_DATA."""
    import random as random_module

    monkeypatch.setattr(model_manager_module, "predict_memory", _make_insufficient_predict())

    random_calls = []
    original_random = random_module.random

    def tracking_random():
        random_calls.append(1)
        return original_random()

    with patch("app.agents.prediction.random.random", side_effect=tracking_random):
        agent = PredictionAgent()
        result = await agent._predict_memory("svc-test", 60)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert len(random_calls) == 0, (
        f"random.random() was called {len(random_calls)} times — "
        "stochastic fallback must not fire on InsufficientDataError"
    )


# ─── Test 3: successful CPU prediction ───────────────────────────────────────

async def test_cpu_successful_prediction(monkeypatch):
    """history >= MIN_HISTORY → status SUCCESS, prediction_source == 'model'."""
    monkeypatch.setattr(model_manager_module, "predict_cpu", _make_successful_predict(62.5))

    agent = PredictionAgent()
    result = await agent._predict_cpu("svc-test", 60)

    assert result["status"] == "SUCCESS"
    assert result["prediction_source"] == "model"
    assert result["predicted_value"] == 62.5
    # ML model metrics must be populated with actual values
    assert "mae" in result["model_metrics"]
    assert "rmse" in result["model_metrics"]
    assert "r2" in result["model_metrics"]
    # Raw historical values and feature matrix must be present
    assert len(result["historical_metrics"]) > 0
    assert len(result["feature_vector"]) > 0
    # Structural sanity
    assert 0.0 <= result["failure_probability"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


# ─── Test 4: successful memory prediction ────────────────────────────────────

async def test_memory_successful_prediction(monkeypatch):
    """history >= MIN_HISTORY (memory) → status SUCCESS, prediction_source == 'model'."""
    monkeypatch.setattr(model_manager_module, "predict_memory", _make_successful_predict(58.0))

    agent = PredictionAgent()
    result = await agent._predict_memory("svc-test", 60)

    assert result["status"] == "SUCCESS"
    assert result["prediction_source"] == "model"
    assert result["predicted_value"] == 58.0
    assert "mae" in result["model_metrics"]
    assert "rmse" in result["model_metrics"]
    assert "r2" in result["model_metrics"]
    assert len(result["historical_metrics"]) > 0
    assert len(result["feature_vector"]) > 0
    assert 0.0 <= result["failure_probability"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0


# ─── Test 5: Twin synchronisation success ─────────────────────────────────────

async def test_twin_sync_called_on_successful_prediction(monkeypatch):
    """After a SUCCESS prediction, update_twin_predicted_state must be called
    with the correct payload keys.
    """
    from app.services.prediction_service import PredictionService
    import app.services.backend_client as backend_client_module

    # Stub the entire LangGraph workflow to return a known SUCCESS analysis
    fake_analysis = {
        "predicted_value": 72.0,
        "confidence": 0.88,
        "failure_probability": 0.12,
        "risk_level": "medium",
        "risk_factors": ["CPU trending up"],
        "recommended_action": "Monitor closely",
        "model_metrics": {"mae": 1.1, "rmse": 1.4, "r2": 0.93},
        "status": "SUCCESS",
        "historical_metrics": [60.0, 65.0, 70.0, 72.0],
        "feature_vector": [[60.0, 65.0, 70.0, 72.0]],
        "prediction_source": "model",
    }

    async def fake_graph_invoke(state):
        state["prediction_analysis"] = fake_analysis
        return state

    # Track calls to update_twin_predicted_state
    sync_calls = []

    async def fake_update_twin(service_id, predicted_state):
        sync_calls.append({"service_id": service_id, "predicted_state": predicted_state})
        return {}

    svc = PredictionService.__new__(PredictionService)
    svc.monitoring_agent = AsyncMock()
    svc.prediction_agent = AsyncMock()
    svc.graph = MagicMock()
    svc.graph.ainvoke = fake_graph_invoke

    monkeypatch.setattr(backend_client_module.backend_client, "update_twin_predicted_state", fake_update_twin)

    result = await svc.predict("svc-abc-123", "cpu", 60)

    # Prediction result must reflect SUCCESS
    assert result.status == "SUCCESS"
    assert result.prediction_source == "model"
    assert result.predicted_value == 72.0

    # Twin sync must have been called exactly once
    assert len(sync_calls) == 1, f"Expected 1 twin sync call, got {len(sync_calls)}"

    synced_payload = sync_calls[0]["predicted_state"]
    assert synced_payload["predicted_value"] == 72.0
    assert synced_payload["failure_probability"] == 0.12
    assert synced_payload["prediction_source"] == "model"
    assert synced_payload["horizon_minutes"] == 60
    assert synced_payload["prediction_type"] == "cpu"
    # Timestamp must be present
    assert "prediction_timestamp" in synced_payload


# ─── Test 6: Twin synchronisation failure ─────────────────────────────────────

async def test_twin_sync_failure_is_reported_honestly(monkeypatch):
    """If the twin sync call fails, the prediction result must still carry
    status SUCCESS with the sync error surfaced in model_metrics, NOT masked.
    """
    from app.services.prediction_service import PredictionService
    import app.services.backend_client as backend_client_module

    fake_analysis = {
        "predicted_value": 55.0,
        "confidence": 0.82,
        "failure_probability": 0.08,
        "risk_level": "low",
        "risk_factors": [],
        "recommended_action": "Continue monitoring",
        "model_metrics": {"mae": 0.9, "rmse": 1.1, "r2": 0.95},
        "status": "SUCCESS",
        "historical_metrics": [50.0, 52.0, 54.0, 55.0],
        "feature_vector": [[50.0, 52.0, 54.0, 55.0]],
        "prediction_source": "model",
    }

    async def fake_graph_invoke(state):
        state["prediction_analysis"] = fake_analysis
        return state

    async def failing_update_twin(service_id, predicted_state):
        raise ConnectionError("Backend twin API unreachable")

    svc = PredictionService.__new__(PredictionService)
    svc.monitoring_agent = AsyncMock()
    svc.prediction_agent = AsyncMock()
    svc.graph = MagicMock()
    svc.graph.ainvoke = fake_graph_invoke

    monkeypatch.setattr(backend_client_module.backend_client, "update_twin_predicted_state", failing_update_twin)

    result = await svc.predict("svc-abc-456", "memory", 60)

    # Prediction itself must still succeed — sync failure must NOT change status
    assert result.status == "SUCCESS", (
        f"Expected status SUCCESS after sync failure, got {result.status!r}"
    )
    assert result.predicted_value == 55.0

    # The sync error must be surfaced in model_metrics
    assert "twin_sync_error" in result.model_metrics, (
        "sync failure must be recorded in model_metrics['twin_sync_error']"
    )
    assert "Backend twin API unreachable" in result.model_metrics["twin_sync_error"]


# ─── Test 7: existing test still passes (regression guard) ───────────────────

async def test_existing_insufficient_data_contract(monkeypatch):
    """Preserve the original test contract from test_prediction_insufficient_data.py."""
    agent = PredictionAgent()

    def fake_predict_cpu(service_id, horizon):
        raise InsufficientDataError("Not enough data")

    monkeypatch.setattr(model_manager_module, "predict_cpu", fake_predict_cpu)

    result = await agent._predict_cpu("svc-123", 360)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["predicted_value"] == 0.0
    assert result["failure_probability"] == 0.0
    assert result["recommended_action"] == "Insufficient historical data for a reliable prediction"
