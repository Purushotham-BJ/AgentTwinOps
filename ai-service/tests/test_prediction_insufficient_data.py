import pytest

from app.agents.prediction import PredictionAgent
from app.services.model_manager import InsufficientDataError
import app.services.model_manager as model_manager


@pytest.mark.asyncio
async def test_prediction_agent_returns_insufficient_data(monkeypatch):
    agent = PredictionAgent()

    def fake_predict_cpu(service_id, horizon):
        raise InsufficientDataError("Not enough data")

    monkeypatch.setattr(model_manager, "predict_cpu", fake_predict_cpu)

    result = await agent._predict_cpu("svc-123", 360)

    assert result["status"] == "INSUFFICIENT_DATA"
    assert result["predicted_value"] == 0.0
    assert result["failure_probability"] == 0.0
    assert result["recommended_action"] == "Insufficient historical data for a reliable prediction"
