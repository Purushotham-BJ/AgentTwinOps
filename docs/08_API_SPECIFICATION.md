# API Specification

---

# Authentication APIs

POST /api/auth/login

POST /api/auth/logout

POST /api/auth/register

GET /api/auth/profile

---

# Infrastructure APIs

GET /api/infrastructure

GET /api/infrastructure/{id}

POST /api/infrastructure

PUT /api/infrastructure/{id}

DELETE /api/infrastructure/{id}

---

# Metrics APIs

GET /api/metrics

GET /api/metrics/live

GET /api/metrics/history

---

# Digital Twin APIs

GET /api/twins

GET /api/twins/{id}

POST /api/twins/sync

POST /api/twins/create

---

# Prediction APIs

POST /api/v1/predict/cpu

POST /api/v1/predict/memory

POST /api/v1/predict/failure

Each request contains `service_id` and `horizon_minutes` (30–1440 minutes).
Responses contain `status`, `prediction_source`, `historical_metrics`,
`feature_vector`, and `model_metrics`. `INSUFFICIENT_DATA` is returned when the
service has fewer than 30 historical records. Successful CPU and memory
predictions synchronize `Twin.predicted_state` through the backend API.

---

# Simulation APIs

POST /api/v1/simulate

Request fields:

- `service_id` (required): an existing infrastructure service UUID
- `scenario`: `cpu_spike`, `traffic_surge`, `database_failure`, `pod_eviction`, or `custom`
- `parameters`: optional absolute `cpu_usage`, `memory_usage`, `latency_ms`, and `status` changes
- `horizon_minutes`: optional 1–1440 minute projection horizon

The response includes `baseline_state`, `simulated_state`,
`simulated_health_score`, `simulated_failure_probability`,
`simulated_operational_status`, and deterministic `impact_summary` values.
Unknown services return `404`. The endpoint is transient and does not mutate
infrastructure, metrics, `current_state`, or `predicted_state`.

---

# Recommendation APIs

GET /api/recommendations

POST /api/recommendations/generate

---

# Incident APIs

GET /api/incidents

POST /api/incidents

PUT /api/incidents/{id}

---

# Dashboard APIs

GET /api/dashboard

GET /api/dashboard/overview

GET /api/dashboard/health

---

# API Standards

Authentication

JWT Bearer Token

Response Format

{
    "success": true,
    "message": "",
    "data": {}
}

Status Codes

200

201

400

401

403

404

500
