# QuickStart — AI Service Integration

## Architecture

```
React Frontend (port 5173)
    ↓
AI Service (port 8001) ← NEW
    ↓
LangGraph Multi-Agent System
    ├── Monitoring Agent
    ├── Prediction Agent
    ├── Simulation Agent
    ├── Recovery Agent
    └── Recommendation Agent
    
Backend API (port 8000) ← UNTOUCHED
    ↓
PostgreSQL
```

## 1. Start AI Service

```powershell
cd ai-service
.\start.ps1
```

Or manually:

```powershell
cd ai-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

## 2. Verify AI Service

Open: http://localhost:8001/docs

You should see:
- Swagger UI with all AI endpoints
- Health check at `/health`
- Predictions, simulations, recommendations, twins endpoints

## 3. Start Backend (if not running)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

## 4. Start Frontend

```powershell
cd frontend
npm run dev
```

Open: http://localhost:5173

## Testing the Integration

### Test Prediction
```powershell
curl -X POST http://localhost:8001/api/v1/predict/cpu `
  -H "Content-Type: application/json" `
  -d '{"service_id":"svc_001","horizon_minutes":360}'
```

### Test Simulation
```powershell
curl -X POST http://localhost:8001/api/v1/simulate `
  -H "Content-Type: application/json" `
  -d '{"scenario":"cpu_spike","service_id":"svc_001","parameters":{}}'
```

### Test Recommendations
```powershell
curl http://localhost:8001/api/v1/recommendations
```

### Test Digital Twins
```powershell
curl http://localhost:8001/api/v1/twins
```

## Frontend Connection

The frontend services now connect to AI service automatically:
- `predictionService.ts` → `POST /api/v1/predict/*`
- `simulationService.ts` → `POST /api/v1/simulate`
- `recommendationService.ts` → `GET /api/v1/recommendations`
- `twinService.ts` → `GET /api/v1/twins`

## Development Mode

Without AI provider API keys, the service uses:
- Deterministic prediction algorithms
- Simulated failure scenarios
- Rule-based recommendations
- Real Digital Twin logic

All responses follow the same schema as production AI.

## Adding AI Provider Keys (Optional)

Edit `ai-service/.env`:

```env
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
```

Restart the AI service to enable LLM-powered enhancements.

## Verification Checklist

- [ ] AI service starts on port 8001
- [ ] Backend remains on port 8000
- [ ] Frontend connects to both services
- [ ] Swagger docs accessible at http://localhost:8001/docs
- [ ] No modifications to `backend/` directory
- [ ] Frontend build passes: `npm run build`
- [ ] All AI endpoints return valid responses

## Architecture Notes

- AI service is **completely separate** from backend
- Backend remains **READ-ONLY** — no modifications
- Frontend calls AI service for predictions/simulations/recommendations
- Backend handles authentication, infrastructure CRUD, incidents
- AI service fetches infrastructure data via backend API
