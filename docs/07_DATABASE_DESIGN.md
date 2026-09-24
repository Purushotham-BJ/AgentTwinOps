# Database Design

---

# Database Architecture

PostgreSQL

Stores

- Users
- Infrastructure
- Incidents

MongoDB

Stores

- Twin Objects
- Historical Metrics
- Simulations
- Recommendations

Redis

Stores

- Cache
- Sessions
- Live Metrics

---

# Schema Authority Note

The physical PostgreSQL primary-key column for all core entities (`users`, `infrastructure`, `incidents`) is `id` (UUID).

Domain-specific names such as `service_id` and `incident_id` are used in foreign-key relationships and API contracts, not as physical primary-key columns.

The Python models may expose read-only property aliases (e.g., `service_id → id`, `incident_id → id`) for application-layer compatibility.

`created_at` and `updated_at` are persistent lifecycle fields present on all three core tables.

---

# Users Table

Fields

id (UUID, PRIMARY KEY — physical PostgreSQL column)

name

email (UNIQUE)

password

role (ENUM: admin, user, operator)

created_at

updated_at

Note: The Python model does not expose a `user_id` property alias. The physical database column is `id`.

---

# Infrastructure Table

Fields

id (UUID, PRIMARY KEY — physical PostgreSQL column)

service_name

service_type

status (ENUM: active, inactive, degraded, healthy, unhealthy)

host

created_at

updated_at

Note: The Python model exposes `service_id` as a read-only property alias for `id`. This alias is available at the application layer; the physical database column is `id`.

---

# Metrics Collection

metric_id

service_id

cpu_usage

memory_usage

disk_usage

network_usage

latency

timestamp

---

# Digital Twin Collection

twin_id

service_id

current_state

predicted_state

health_score

failure_probability

last_sync

---

# Simulation Collection

simulation_id

scenario

input_parameters

results

created_at

---

# Recommendation Collection

recommendation_id

service_id

recommendation_type

priority

description

status

created_at

---

# Incident Table

Fields

id (UUID, PRIMARY KEY — physical PostgreSQL column)

service_id (UUID, NOT NULL — FK → infrastructure.id, ON DELETE RESTRICT)

severity (ENUM: low, medium, high, critical)

incident_type

resolution_status (ENUM: open, in_progress, resolved, closed)

timestamp

created_at

updated_at

Note: The Python model exposes `incident_id` as a read-only property alias for `id`. This alias is available at the application layer; the physical database column is `id`.

Foreign Key

incidents.service_id → infrastructure.id

ON DELETE RESTRICT

---

# Entity Relationships

User

↓

Infrastructure

↓

Metrics

↓

Twin

↓

Prediction

↓

Recommendation

↓

Simulation
