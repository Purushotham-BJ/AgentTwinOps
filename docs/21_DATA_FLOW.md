# Data Flow Design

---

# DFD Level 0

Users

↓

AgentTwinOps

↓

Infrastructure Monitoring

↓

Digital Twin

↓

Prediction

↓

Simulation

↓

Recommendations

↓

Reports

---

# DFD Level 1

Infrastructure

↓

Prometheus

↓

Metrics Collector

↓

Data Normalizer

↓

Metric Repository

↓

Digital Twin Repository

↓

Prediction Engine

↓

Recommendation Engine

↓

Dashboard

---

# DFD Level 2

Infrastructure

↓

Node Exporter

↓

Prometheus

↓

Metrics API

↓

Metrics Service

↓

Twin Synchronizer

↓

Twin Repository

↓

Prediction Engine

↓

Simulation Engine

↓

Recommendation Engine

↓

Frontend Dashboard

---

# Data Sources

Prometheus

Node Exporter

cAdvisor

Infrastructure Metadata

Simulation Inputs

---

# Data Stores

PostgreSQL

MongoDB

Redis

Twin Repository

Historical Metrics

Simulation Results

Recommendations

---

# Data Outputs

Dashboard

Reports

Incident Alerts

Prediction Charts

Simulation Results

Recommendation Reports

---

# Data Flow Rules

No module directly accesses infrastructure.

All communication goes through the Metrics Layer.

Digital Twin never directly modifies infrastructure.

Predictions never overwrite real metrics.

Simulations always use Twin Objects.