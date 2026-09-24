# System Architecture

---

# Overview

The project follows a layered cloud-native architecture.

```
                     React Dashboard
                             │
                             ▼
                     FastAPI Backend
                             │
───────────────────────────────────────────────
         Digital Twin Framework
───────────────────────────────────────────────
│ Digital Twin Repository                    │
│ Prediction Engine                          │
│ Simulation Engine                          │
│ Recommendation Engine                      │
───────────────────────────────────────────────
                 Multi-Agent Layer
───────────────────────────────────────────────
│ Monitoring Agent                           │
│ Prediction Agent                           │
│ Recovery Agent                             │
│ Cost Agent                                 │
│ Incident Agent                             │
───────────────────────────────────────────────
             Metrics Collection Layer
───────────────────────────────────────────────
Prometheus
Node Exporter
cAdvisor
───────────────────────────────────────────────
             Real Infrastructure
───────────────────────────────────────────────
Docker Containers
Kubernetes Pods
MongoDB
PostgreSQL
Redis
AWS EC2
```

---

# Layer Descriptions

Presentation Layer

React Dashboard

Business Layer

FastAPI

Digital Twin Layer

Maintains synchronized infrastructure models.

AI Layer

Prediction and recommendation.

Monitoring Layer

Collects real-time metrics.

Infrastructure Layer

Real cloud deployment.

---

# Communication

React → FastAPI → Twin Engine

Twin Engine → Prediction Engine

Prediction Engine → Recommendation Engine

Recommendation Engine → Dashboard

Monitoring → Twin Repository

---

# Design Principles

Loose Coupling

High Cohesion

Microservice Friendly

Cloud Native

Scalable

Modular
