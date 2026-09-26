# Model manager for AI Service predictions
"""
Provides functions to train, load, and predict CPU and Memory usage using
scikit-learn models. Models are persisted under ``ai-service/models/``.
If insufficient historical data is available, the manager raises
``InsufficientDataError`` which the caller can handle gracefully.
"""
import os
import joblib
from pathlib import Path
from typing import List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.services.backend_client import backend_client
from app.config.settings import settings

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MIN_HISTORY = getattr(settings, "PREDICTION_MIN_HISTORY", 30)  # minimum records
HORIZON_DEFAULT = getattr(settings, "PREDICTION_HORIZON_MINUTES", 60)

class InsufficientDataError(RuntimeError):
    pass

def _ensure_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

def _model_path(metric: str) -> Path:
    return MODEL_DIR / f"{metric}_model.joblib"

def _prepare_features(values: List[float]) -> Tuple[np.ndarray, np.ndarray]:
    """Create simple lag features for time‑series regression.
    Returns X (features) and y (targets).
    """
    if len(values) < 5:
        raise InsufficientDataError("Not enough data points for feature creation")
    # Use previous 4 points to predict next point
    X, y = [], []
    for i in range(4, len(values)):
        X.append(values[i-4:i])
        y.append(values[i])
    return np.array(X), np.array(y)

def _train_regressor(metric: str, values: List[float]) -> RandomForestRegressor:
    X, y = _prepare_features(values)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def _save_model(metric: str, model: RandomForestRegressor):
    _ensure_model_dir()
    joblib.dump(model, _model_path(metric))

def _load_model(metric: str) -> RandomForestRegressor:
    path = _model_path(metric)
    if not path.exists():
        raise FileNotFoundError(f"Model for {metric} not found")
    return joblib.load(path)

def _fetch_metric_history(service_id: str, metric_name: str) -> List[float]:
    """Retrieve historical metric values from the backend.
    ``metric_name`` should be one of ``cpu``, ``memory``, ``disk``, ``network``, ``latency``.
    Returns a list of float values ordered by timestamp (oldest → newest).
    """
    # The backend metrics API returns keys like "cpu_usage", "memory_usage", etc.
    # Map the logical metric name to the actual field name in the API response.
    _FIELD_MAP = {
        "cpu": "cpu_usage",
        "memory": "memory_usage",
        "disk": "disk_usage",
        "network": "network_usage",
        "latency": "latency",
    }
    field_name = _FIELD_MAP.get(metric_name, metric_name)

    try:
        raw_metrics = backend_client.get_metrics(service_id)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch metrics: {e}")

    values = [
        float(m[field_name])
        for m in raw_metrics
        if field_name in m and m[field_name] is not None
    ]
    return values

def get_or_train_model(metric: str, service_id: str) -> RandomForestRegressor:
    """Return a trained model for ``metric`` (cpu or memory).
    If a persisted model exists, load it; otherwise train a new one using
    historical data for the given ``service_id``.
    """
    try:
        return _load_model(metric)
    except FileNotFoundError:
        # Need to train
        values = _fetch_metric_history(service_id, metric)
        if len(values) < MIN_HISTORY:
            raise InsufficientDataError(f"Only {len(values)} records; need {MIN_HISTORY}")
        model = _train_regressor(metric, values)
        _save_model(metric, model)
        return model

def predict(metric: str, service_id: str, horizon_minutes: int = HORIZON_DEFAULT) -> Tuple[float, dict, List[List[float]], List[float]]:
    """Predict a future value for ``metric``.
    Returns a tuple of (predicted_value, metrics_dict, feature_matrix, raw_values).
    """
    values = _fetch_metric_history(service_id, metric)
    if len(values) < MIN_HISTORY:
        raise InsufficientDataError("Insufficient historical data for prediction")
    # Train a fresh model on all data for simplicity (could load persisted)
    model = _train_regressor(metric, values)
    # Evaluate on last 20% as validation
    split = int(0.8 * len(values))
    X_train, y_train = _prepare_features(values[:split])
    X_val, y_val = _prepare_features(values[split:])
    model.fit(X_train, y_train)
    preds = model.predict(X_val)
    mae = mean_absolute_error(y_val, preds)
    rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
    r2 = r2_score(y_val, preds)
    # Forecast using most recent 4 points
    recent = np.array(values[-4:]).reshape(1, -1)
    future = model.predict(recent)[0]
    future = max(0.0, min(100.0, float(future)))
    metrics = {"mae": mae, "rmse": rmse, "r2": r2}
    # Full feature matrix for all data
    full_X, _ = _prepare_features(values)
    return future, metrics, full_X.tolist(), values

# Expose convenience functions
def predict_cpu(service_id: str, horizon_minutes: int = HORIZON_DEFAULT):
    return predict("cpu", service_id, horizon_minutes)

def predict_memory(service_id: str, horizon_minutes: int = HORIZON_DEFAULT):
    return predict("memory", service_id, horizon_minutes)

"""Note:
- Model persistence is optional; we train on‑demand to keep the example lightweight.
- For a production system you would schedule periodic retraining and version the models.
"""
