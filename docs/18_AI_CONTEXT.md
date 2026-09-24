# AI Context

If you are an AI assistant working on this project, read this file before generating any code.

---

Project Name

AgentTwinOps

---

Project Goal

Build a Digital Twin of cloud infrastructure capable of:

- Monitoring
- Prediction
- Simulation
- Recommendation

using AI and Multi-Agent Systems.

---

Project Scope

This project is NOT a cloud monitoring dashboard.

It is NOT Grafana.

It is NOT Prometheus.

It is NOT an AWS management system.

Instead,

it creates synchronized Digital Twins of cloud infrastructure.

---

Core Concepts

Digital Twin

Every infrastructure component has a virtual model.

Multi-Agent

Multiple AI agents collaborate.

Prediction

Infrastructure failures are predicted.

Simulation

"What-if" scenarios are executed.

Recommendation

Suggestions are generated but never automatically executed.

---

Architecture

React

↓

FastAPI

↓

Digital Twin

↓

Prediction Engine

↓

Simulation

↓

Recommendation

↓

Dashboard

---

Rules

Never replace FastAPI.

Never replace React.

Always use PostgreSQL + MongoDB + Redis.

Never remove the Digital Twin layer.

Every infrastructure component must have a Twin Object.

Never implement automatic infrastructure modification.

Recommendations require human approval.

---

Current Progress

Documentation Phase

No implementation yet.

---

Coding Rules

Follow project architecture.

Do not introduce unnecessary frameworks.

Prefer modular design.

Avoid hardcoding.

Write production-quality code.

Document every public function.
