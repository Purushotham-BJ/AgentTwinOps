# Sequence Diagrams

---

# Login Sequence

User

↓

Frontend

↓

Authentication API

↓

Database

↓

JWT Generated

↓

Frontend

↓

Dashboard

---

# Metric Synchronization

Prometheus

↓

Metrics Collector

↓

Twin Synchronizer

↓

Twin Repository

↓

Dashboard

---

# Prediction Sequence

Metrics

↓

Prediction Engine

↓

ML Model

↓

Prediction Database

↓

Recommendation Engine

↓

Dashboard

---

# Simulation Sequence

User

↓

Simulation API

↓

Twin Repository

↓

Simulation Engine

↓

Simulation Results

↓

Dashboard

---

# Recommendation Sequence

Prediction Engine

↓

Recovery Agent

↓

Cost Agent

↓

Recommendation Agent

↓

Dashboard

---

# Dashboard Refresh

Dashboard

↓

Backend

↓

Twin Repository

↓

Prediction Repository

↓

Simulation Repository

↓

Dashboard Updated