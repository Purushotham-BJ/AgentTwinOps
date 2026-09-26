# Multi-Agent System Design

---

# Overview

AgentTwinOps uses a Multi-Agent System (MAS) where multiple intelligent software agents collaborate to monitor, analyze, predict, and optimize cloud infrastructure.

Each agent has a single responsibility and communicates with other agents through the Agent Coordinator.

This modular architecture improves scalability, maintainability, and extensibility.

---

# Agent Architecture

```
                 Agent Coordinator
                         │
 ┌─────────────┬──────────┼──────────────┬─────────────┐
 │             │          │              │             │
 ▼             ▼          ▼              ▼             ▼
Monitoring  Prediction  Simulation  Recovery   Cost Optimization
 Agent        Agent        Agent       Agent         Agent
                         │
                         ▼
                  Recommendation Agent
```

                  ## Sprint 9 Operations Coordinator

                  `POST /api/v1/agents/orchestrate` runs one deterministic, authenticated
                  workflow for a real service. It fetches the service, latest metric, Twin, and
                  associated incidents once, then passes a serializable context through
                  Monitoring, Prediction, Recommendation, Simulation, and Recovery stages.
                  Prediction uses the pure Prediction Agent and does not persist Twin state;
                  simulation is transient; recovery returns proposal-only actions requiring
                  human approval.

                  Routing is stable: monitoring and recommendation always run, prediction runs
                  when enabled, simulation runs for WARNING/CRITICAL state, and recovery emits
                  actions only for non-healthy state. Each stage reports SUCCESS, SKIPPED, or
                  FAILED and optional failures are isolated.

---

# Agent 1: Monitoring Agent

Purpose

Continuously monitor cloud infrastructure.

Responsibilities

- Fetch Prometheus metrics
- Detect unavailable services
- Update Digital Twin Repository
- Generate heartbeat signals

Inputs

- Prometheus API
- Node Exporter
- cAdvisor

Outputs

- Updated Twin Objects

Execution Frequency

Every 5 seconds

---

# Agent 2: Prediction Agent

Purpose

Forecast future infrastructure behavior.

Responsibilities

- CPU Prediction
- Memory Prediction
- Latency Prediction
- Failure Probability

Inputs

Historical Metrics

Outputs

Prediction Records

Execution Frequency

Every 30 seconds

---

# Agent 3: Simulation Agent

Purpose

Run hypothetical scenarios.

Supported Simulations

- Traffic spike
- Pod failure
- Memory leak
- Database outage
- API overload

Outputs

Simulation Results

Runs

On demand

---

# Agent 4: Recovery Agent

Purpose

Recommend corrective actions.

Responsibilities

- Restart services
- Scale replicas
- Increase CPU
- Increase Memory

This agent does NOT execute actions automatically.

It only generates recommendations.

---

# Agent 5: Cost Optimization Agent

Purpose

Reduce cloud cost.

Responsibilities

Detect

- Idle containers
- Unused resources
- Oversized instances

Generate

- Cost reduction recommendations

---

# Agent 6: Recommendation Agent

Purpose

Combine outputs from all agents.

Responsibilities

Generate:

- Infrastructure Health Report
- Incident Report
- Recommended Actions

The implemented Recommendation Agent is deterministic and rule-based. It
evaluates real metrics, Digital Twin state, operational status, health,
failure probability, anomalies, and service incidents. It returns deduplicated
actions sorted by criticality and does not execute infrastructure changes.

---

# Agent Communication

Monitoring Agent

↓

Prediction Agent

↓

Simulation Agent

↓

Recovery Agent

↓

Recommendation Agent

↓

Dashboard

---

# Design Principles

- Independent Agents
- Loose Coupling
- Shared Twin Repository
- Event Driven
- Easily Extendable

Future agents can be added without modifying existing agents.
