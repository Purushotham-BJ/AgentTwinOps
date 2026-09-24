# AgentTwinOps Integration Guide

## Architecture Overview

```
Frontend (React)
http://localhost:5173
    │
    ├──→ Backend API (FastAPI)
    │    http://localhost:8000
    │    │
    │    └── PostgreSQL Database
    │
    └──→ AI Service (FastAPI + LangGraph)
         http://localhost:8001
         │
         └──→ Backend API (for data)
              http://localhost:8000
```

## Service Communication

### 1. Frontend → Backend
- **Purpose**: CRUD operations for infrastructure, incidents, users
- **Auth**: JWT tokens (obtained via `/api/v1/auth/login`)
- **Endpoints**:
  - `POST /api/v1/auth/register` - User registration
  - `POST /api/v1/auth/login` - Authentication (returns JWT)
  - `GET /api/v1/auth/profile` - User profile
  - `GET /api/v1/infrastructure` - List infrastructure
  - `POST /api/v1/infrastructure` - Create infrastructure
  - `GET /api/v1/incidents` - List incidents
  - `POST /api/v1/incidents` - Create incident

### 2. Frontend → AI Service
- **Purpose**: AI-powered predictions, simulations, recommendations
- **Auth**: None (internal service)
- **Endpoints**:
  - `POST /api/v1/predict/cpu` - CPU usage prediction
  - `POST /api/v1/predict/memory` - Memory usage prediction
  - `POST /api/v1/predict/failure` - Failure probability
  - `POST /api/v1/simulate` - Run scenario simulation
  - `GET /api/v1/recommendations` - Get AI recommendations
  - `GET /api/v1/twins` - Get digital twins
  - `GET /api/v1/twins/{id}` - Get specific twin

### 3. AI Service → Backend
- **Purpose**: Fetch real infrastructure and incident data
- **Auth**: Optional JWT token (via `BACKEND_API_TOKEN` env var)
- **Implementation**: `ai-service/app/services/backend_client.py`
- **Fallback**: Uses mock data when backend unavailable

## Backend Client Integration

The AI service integrates with the backend via `BackendClient`:

```python
from app.services.backend_client import backend_client

# Fetch infrastructure
infrastructure = await backend_client.get_infrastructure()
# Returns: List[Dict] from backend API /api/v1/infrastructure

# Fetch incidents  
incidents = await backend_client.get_incidents()
# Returns: List[Dict] from backend API /api/v1/incidents

# Fetch specific service
service = await backend_client.get_infrastructure_by_id(service_id)
# Returns: Dict from backend API /api/v1/infrastructure/{id}
```

### Response Format

Backend API returns data in this envelope:

```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 10
  },
  "timestamp": "2026-09-01T20:00:00Z"
}
```

The `BackendClient` automatically extracts the `items` array.

### Authentication

If the backend requires authentication for AI service requests:

1. Obtain a JWT token from the backend (via `/api/v1/auth/login`)
2. Set it in `ai-service/.env`:
   ```
   BACKEND_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
3. The `BackendClient` automatically includes it in requests:
   ```
   Authorization: Bearer <token>
   ```

### Fallback Behavior

When the backend is unavailable (network error, not running, auth failure):
- The `BackendClient` catches `httpx.HTTPError`
- Returns mock data for development
- Logs warning but doesn't crash
- AI service remains operational with simulated data

## Data Flow Examples

### Example 1: CPU Prediction

```
1. Frontend sends: POST /api/v1/predict/cpu
   {
     "service_id": "svc_001",
     "horizon_minutes": 60
   }

2. AI Service:
   a. Fetches infrastructure via backend_client.get_infrastructure()
   b. Runs monitoring agent to analyze current state
   c. Runs prediction agent using LangGraph workflow
   d. Returns prediction with confidence score

3. Frontend receives:
   {
     "success": true,
     "data": {
       "id": "...",
       "service_id": "svc_001",
       "prediction_type": "cpu",
       "predicted_value": 67.5,
       "confidence": 0.85,
       "risk_level": "medium",
       "data_points": [...]
     }
   }
```

### Example 2: Digital Twin Sync

```
1. Frontend requests: GET /api/v1/twins

2. AI Service:
   a. Calls backend_client.get_infrastructure()
   b. For each infrastructure item:
      - Fetches current metrics from backend
      - Generates predictions via prediction_service
      - Calculates health score
      - Builds twin object
   
3. Frontend receives real-time digital twins with:
   - Current state (from backend)
   - Predicted state (from AI)
   - Health scores
   - Sync status
```

### Example 3: Recommendations

```
1. Frontend requests: GET /api/v1/recommendations

2. AI Service:
   a. Fetches infrastructure via backend_client
   b. Fetches incidents via backend_client
   c. Runs multi-agent workflow:
      - MonitoringAgent: analyzes current state
      - PredictionAgent: forecasts issues
      - RecoveryAgent: identifies problems
      - RecommendationAgent: suggests actions
   d. Returns prioritized recommendations

3. Frontend displays actionable recommendations
```

## Setup Instructions

### 1. Start Backend

```powershell
cd backend
# Ensure PostgreSQL is running
# Set DATABASE_URL in backend/.env
pip install -r requirements.txt
uvicorn app.core.factory:create_app --factory --port 8000
```

Backend will be available at http://localhost:8000

### 2. Start AI Service

```powershell
cd ai-service
# Copy and configure environment
cp .env.example .env
# Install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Start service
python -m uvicorn app.main:app --reload --port 8001
```

AI service will be available at http://localhost:8001

### 3. Start Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/agenttwinops
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:5173"]
```

### AI Service (.env)
```bash
# Backend integration
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TOKEN=  # Optional JWT token

# AI providers (optional for dev)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model config
AI_MODEL=gpt-4o-mini
ENABLE_REAL_ML_MODELS=false
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_AI_SERVICE_URL=http://localhost:8001
```

## Testing the Integration

### 1. Test Backend API
```powershell
# Register user
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/v1/auth/register `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"name":"Test User","email":"test@example.com","password":"Test123!@#"}'

# Login
$auth = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/v1/auth/login `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"email":"test@example.com","password":"Test123!@#"}'

$token = $auth.data.access_token

# Get infrastructure (with auth)
Invoke-RestMethod -Method GET -Uri http://localhost:8000/api/v1/infrastructure `
  -Headers @{"Authorization"="Bearer $token"}
```

### 2. Test AI Service
```powershell
# Health check
Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/health

# CPU prediction
Invoke-RestMethod -Method POST -Uri http://localhost:8001/api/v1/predict/cpu `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"service_id":"svc_001","horizon_minutes":60}'

# Get digital twins
Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/twins

# Get recommendations
Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/recommendations
```

### 3. Test End-to-End Flow
1. Open frontend at http://localhost:5173
2. Register/login via UI
3. Navigate to Infrastructure → view services
4. Navigate to AI → view predictions, twins, recommendations
5. Verify data flows from Backend → AI Service → Frontend

## Troubleshooting

### Backend Connection Issues
- **Symptom**: AI service logs "Backend connection failed"
- **Solution**: 
  - Verify backend is running on port 8000
  - Check `BACKEND_API_URL` in ai-service/.env
  - If auth required, set `BACKEND_API_TOKEN`
  - AI service will use mock data as fallback

### Database Not Running
- **Symptom**: Backend fails with "Connection refused" to PostgreSQL
- **Solution**:
  - Start PostgreSQL: `docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres`
  - Or install PostgreSQL locally
  - Update `DATABASE_URL` in backend/.env
  - Run migrations: `cd backend && alembic upgrade head`

### CORS Errors
- **Symptom**: Browser console shows CORS policy error
- **Solution**:
  - Backend: Add frontend URL to `CORS_ORIGINS` in .env
  - AI Service: Add frontend URL to `CORS_ORIGINS` in .env
  - Restart both services

### AI Predictions Return Zeros
- **Symptom**: Predictions show 0.0 values
- **Solution**: This is expected behavior without:
  - Real infrastructure data (needs backend + database)
  - AI API keys (OpenAI or Anthropic)
  - Set `ENABLE_REAL_ML_MODELS=true` after adding API keys

## Architecture Decisions

### Why Two Services?

**Backend (Port 8000)**:
- Traditional CRUD operations
- Database persistence
- User authentication
- Infrastructure/incident management
- Battle-tested FastAPI + SQLAlchemy stack

**AI Service (Port 8001)**:
- AI/ML workloads (predictions, simulations)
- LangGraph multi-agent orchestration
- Stateless predictions
- Can scale independently
- Isolates AI dependencies

### Why Backend Client?

The AI service needs real infrastructure data for accurate predictions. Instead of:
- ❌ Duplicating database access
- ❌ Sharing database connection
- ❌ Creating tight coupling

We use:
- ✅ HTTP API client (loose coupling)
- ✅ Backend owns the data model
- ✅ AI service consumes via API
- ✅ Graceful fallback to mock data

## Next Steps

1. **Production Deployment**:
   - Add service mesh for inter-service communication
   - Implement API gateway
   - Add rate limiting
   - Enable HTTPS

2. **Enhanced Integration**:
   - Real-time updates via WebSockets
   - Event-driven architecture (Kafka/RabbitMQ)
   - Distributed tracing (OpenTelemetry)
   - Centralized logging (ELK stack)

3. **AI Enhancements**:
   - Train ML models on real infrastructure data
   - Implement model versioning
   - Add A/B testing for predictions
   - Enable online learning

4. **Monitoring**:
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Implement health checks
   - Add alerting (PagerDuty, Slack)
