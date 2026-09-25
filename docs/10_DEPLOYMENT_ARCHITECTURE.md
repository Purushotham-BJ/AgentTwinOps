# Deployment Architecture

---

# Overview

AgentTwinOps is designed as a cloud-native application deployed on AWS using Docker and Kubernetes.

The system follows a modular deployment architecture where each major component runs independently inside containers.

The repository's verified local runtime is Docker Compose. A production-oriented Kubernetes structure is provided
under `k8s/`, but it requires a configured cluster, an image registry, domain/TLS configuration, and a populated
Secret before it can be applied.

---

# Deployment Goals

- Modular Deployment
- High Availability
- Containerized Services
- Easy Scaling
- Easy Maintenance
- Cloud Native Design

---

# Infrastructure Architecture

                    Internet
                        │
                AWS EC2 Instance
                        │
                  Nginx Reverse Proxy
                        │
────────────────────────────────────────────
        Kubernetes Cluster (Minikube/K3s)
────────────────────────────────────────────
│                                          │
│ React Frontend                           │
│ FastAPI Backend                          │
│ Authentication Service                   │
│ Digital Twin Service                     │
│ Prediction Service                       │
│ Simulation Service                       │
│ Recommendation Service                   │
│ PostgreSQL                              │
│ Persistent PostgreSQL                   │
│ Redis/monitoring extensions (future)    │
────────────────────────────────────────────

---

# Docker Containers

Frontend Container

Backend Container

AI Service Container

Monitoring Container

PostgreSQL Container

MongoDB Container

Redis Container

Prometheus Container

Grafana Container

---

# Kubernetes Resources

Deployment

Service

ConfigMap

Secret

Ingress

Persistent Volume

Persistent Volume Claim

Namespace

---

# Networking

Browser → Ingress → Frontend
                   ├─ /api → Backend → PostgreSQL
                   └─ /api/v1/{predict,simulate,recommendations,agents}
                                   → AI service → Backend → PostgreSQL

The AI service communicates with PostgreSQL only through the authenticated backend HTTP API.

---

# Environment Variables

DATABASE_URL

MONGODB_URI

REDIS_URL

JWT_SECRET

PROMETHEUS_URL

AWS_ACCESS_KEY

AWS_SECRET_KEY

---

# Monitoring Stack

Prometheus

↓

Node Exporter

↓

cAdvisor

↓

Grafana

↓

AgentTwinOps Dashboard

---

# Backup Strategy

PostgreSQL Daily Backup

MongoDB Daily Backup

Configuration Backup

Logs Backup

---

# Logging

Application Logs

Infrastructure Logs

API Logs

Error Logs

Agent Logs

---

# Security

HTTPS/TLS at the ingress

JWT

RBAC

Kubernetes Secrets

Environment Variables

## Kubernetes rollout status

The manifests in `k8s/` define namespace, persistent PostgreSQL storage, backend migrations and probes,
AI-service probes, frontend service, and ingress routing. They were client-side rendered successfully, but
were not applied in this environment because no Kubernetes API server or AWS account was available.

Firewall Rules
