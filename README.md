# AgentTwinOps

**AI-Powered Digital Twin & Multi-Agent DevOps Platform**

AgentTwinOps is a complete AI-powered platform that combines digital twin technology with multi-agent AI systems to provide intelligent infrastructure monitoring, predictive analytics, and automated recommendations for DevOps operations.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   AI Service     │    │     Backend     │
│   (React)       │────│   (LangGraph)    │────│   (FastAPI)     │
│   Port 5173     │    │   Port 8001      │    │   Port 8000     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              │                         │
                       ┌──────▼──────┐         ┌───────▼────────┐
                       │ Multi-Agent │         │  PostgreSQL    │
                       │   System    │         │  Database      │
                       │ (LangGraph) │         │  Port 5432     │
                       └─────────────┘         └────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**  
- **PostgreSQL 14+**
- **Git**

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd AgentTwinOps
```

### 2. PostgreSQL Setup

1. **Install PostgreSQL** (if not already installed)
2. **Create database:**
   ```sql
   createdb agenttwinops
   ```
3. **Set password for postgres user** (remember this for later)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database password:
# DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/agenttwinops

# Run database migrations
alembic upgrade head

# Start backend
uvicorn app.core.factory:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: **http://localhost:8000**

### 4. AI Service Setup

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment  
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key (optional):
# OPENAI_API_KEY=your_openai_api_key_here

# Start AI service
python -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
```

AI Service will be available at: **http://localhost:8001**

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults should work)

# Start frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## 🔐 Default Login

```
Email: admin@agenttwinops.dev
Password: AdminPass123!@#
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React web application |
| **Backend** | http://localhost:8000 | FastAPI backend + API docs |
| **AI Service** | http://localhost:8001 | AI/ML services + API docs |
| **Database** | localhost:5432 | PostgreSQL database |

## 🤖 AI Features

### Multi-Agent System (LangGraph)

- **Monitoring Agent**: Infrastructure health analysis
- **Prediction Agent**: CPU/Memory/Failure forecasting  
- **Simulation Agent**: What-if scenario modeling
- **Recovery Agent**: Automated recovery recommendations
- **Recommendation Agent**: Intelligent optimization suggestions

### LLM Integration

The system supports OpenAI and Anthropic APIs for enhanced AI capabilities:

```bash
# In ai-service/.env
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Note**: The system works without LLM keys using deterministic algorithms.

## 📊 Core Features

### 🏢 Infrastructure Management
- Real-time service monitoring
- Health status tracking
- Service lifecycle management

### 🔮 AI Predictions
- **CPU Usage Forecasting**: Predict future CPU utilization
- **Memory Usage Forecasting**: Predict memory consumption patterns
- **Failure Risk Analysis**: Calculate failure probabilities

### 🎮 Scenario Simulation
- **CPU Spike Simulation**: Model CPU surge impacts
- **Traffic Surge Simulation**: Analyze traffic increase effects
- **Database Failure Simulation**: Assess database outage impacts

### 💡 AI Recommendations
- Automated infrastructure optimization suggestions
- Proactive issue prevention recommendations
- Resource scaling recommendations

### 🔄 Digital Twin
- Real-time digital representations of infrastructure
- Predictive state modeling
- Health score calculation

## 🗄️ Database

The system uses PostgreSQL with the following tables:

- **users**: Authentication and user management
- **infrastructure**: Service definitions and status
- **incidents**: Issue tracking and resolution
- **alembic_version**: Database schema versioning

### Database Commands

```sql
# Connect to database
psql -h localhost -U postgres -d agenttwinops

# View tables
\dt

# View infrastructure services
SELECT service_name, status, host FROM infrastructure;

# View users
SELECT id, email, is_active, created_at FROM users;
```

## 🛠️ Development

### Backend API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### AI Service API Documentation  
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test

# AI Service tests
cd ai-service
pytest
```

## 🚀 Production Deployment

### Environment Configuration

1. **Set production environment variables**:
   ```bash
   APP_ENV=production
   DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/agenttwinops
   SECRET_KEY=your_strong_production_secret_key
   ```

2. **Configure secure CORS origins**
3. **Set up SSL/TLS certificates**
4. **Configure proper logging**

### Build Commands

```bash
# Frontend production build
cd frontend
npm run build

# Backend production setup
cd backend
pip install -r requirements.txt
alembic upgrade head

# AI Service production setup  
cd ai-service
pip install -r requirements.txt
```

### Docker Support

Docker configurations are available in each service directory.

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database `agenttwinops` exists

2. **AI Service Returns Errors**
   - Verify backend is running on port 8000
   - Check AI service can connect to backend
   - Verify LLM API keys (if using)

3. **Frontend Network Errors**
   - Verify backend and AI service are running
   - Check CORS configuration
   - Verify service URLs in frontend `.env`

### Logs

```bash
# View backend logs
cd backend
tail -f *.log

# View AI service logs  
cd ai-service  
tail -f *.log
```

## 📖 Documentation

- [AI Service Implementation](AI_SERVICE_IMPLEMENTATION.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Quick Start AI](QUICKSTART_AI.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [documentation](docs/)
- Create an issue on GitHub
- Review API documentation at service `/docs` endpoints

---

**AgentTwinOps** - Intelligent Infrastructure Management with AI 🤖