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

GET /api/v1/recommendations

POST /api/v1/recommendations/generate

The endpoints require the caller's backend bearer token and evaluate real
registered services. `infrastructure_ids` may restrict generation to selected
services; unknown IDs return `404`. Responses include `type`, `priority`,
`category`, `reason`, `action`, and deterministic `confidence`. No
recommendation endpoint mutates infrastructure, metrics, or Twin state.

## Multi-Agent Operations API

`POST /api/v1/agents/orchestrate`

The authenticated request accepts a registered `service_id`, optional
`include_prediction`, `include_simulation`, and `include_recovery` flags, and
an optional `horizon_minutes`. The response reports agent execution statuses,
monitoring data, predictions, recommendations, transient simulations,
proposal-only recovery actions, and isolated errors. Unknown services return
`404`; missing authentication returns `401`. The workflow does not mutate
infrastructure, metrics, `Twin.current_state`, or `Twin.predicted_state`.

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
