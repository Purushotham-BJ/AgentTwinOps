# Deployment Architecture

---

# Overview

AgentTwinOps is designed as a cloud-native application deployed on AWS using Docker and Kubernetes.

The system follows a modular deployment architecture where each major component runs independently inside containers.

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
│ MongoDB                                 │
│ Redis                                   │
│ Prometheus                              │
│ Grafana                                │
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

Frontend

↓

Nginx

↓

Backend APIs

↓

Internal Services

↓

Databases

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

HTTPS

JWT

RBAC

Docker Secrets

Environment Variables

Firewall Rules
