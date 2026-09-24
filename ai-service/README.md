# AgentTwinOps AI Service

Standalone AI service for Digital Twin operations using LangGraph multi-agent orchestration.

## Architecture

```
React Frontend
    ↓
AI Service (FastAPI + LangGraph)
    ↓
Multi-Agent System
    ├── Monitoring Agent
    ├── Prediction Agent
    ├── Simulation Agent
    ├── Recovery Agent
    └── Recommendation Agent
```

## Features

- **CPU/Memory/Failure Prediction** — ML-powered forecasting
- **What-if Simulations** — Test scenarios before they happen
- **AI Recommendations** — Intelligent infrastructure suggestions
- **Digital Twins** — Synchronized virtual replicas

## Setup

### 1. Install Dependencies

```bash
cd ai-service
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run Service

```bash
# Development
python -m uvicorn app.main:app --reload --port 8001

# Production
python app/main.py
```

## API Endpoints

### Predictions
- `POST /api/v1/predict/cpu` — Predict CPU usage
- `POST /api/v1/predict/memory` — Predict memory usage
- `POST /api/v1/predict/failure` — Predict failure probability

### Simulations
- `POST /api/v1/simulate` — Run what-if scenario

### Recommendations
- `GET /api/v1/recommendations` — Get all recommendations
- `POST /api/v1/recommendations/generate` — Generate new recommendations

### Digital Twins
- `GET /api/v1/twins` — Get all twins
- `GET /api/v1/twins/{id}` — Get specific twin

### Health
- `GET /health` — Health check

## LangGraph Workflows

### Prediction Workflow
```
Input → Monitoring Agent → Prediction Agent → Output
```

### Simulation Workflow
```
Input → Baseline → Simulation Agent → Impact Analysis → Output
```

### Recommendation Workflow
```
Input → Monitoring → Prediction → Recovery → Recommendation → Output
```

## Development Mode

Without API keys, the service uses deterministic algorithms clearly labeled as development mode. All responses are structured the same way.

## Integration

The frontend connects to this service via:
- `VITE_AI_API_BASE_URL=http://localhost:8001`

Backend remains completely separate at port 8000.

## Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
