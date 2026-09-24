# 🚀 AgentTwinOps Deployment Checklist

## ✅ Pre-Deployment Verification

### Repository Structure
- [x] Backend dependencies (requirements.txt, .env.example)
- [x] AI Service dependencies (requirements.txt, .env.example) 
- [x] Frontend dependencies (package.json, package-lock.json, .env.example)
- [x] Root documentation (README.md, .gitignore)
- [x] Database migrations (alembic configuration)

### Security
- [x] No .env files committed (only .env.example)
- [x] No hardcoded API keys or passwords
- [x] Proper .gitignore protection
- [x] Backend integrity maintained (READ-ONLY constraint respected)

### Configuration
- [x] Frontend uses environment variables for API URLs
- [x] AI Service configured for real backend integration
- [x] All services use configurable ports and hosts

## 🎯 Deployment Steps for New Developer

### 1. System Prerequisites
```bash
# Install required software
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git
```

### 2. Database Setup
```sql
# Create database
createdb agenttwinops

# Set postgres user password (remember for .env)
psql -c "ALTER USER postgres PASSWORD 'your_secure_password';"
```

### 3. Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd AgentTwinOps

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/agenttwinops
alembic upgrade head
uvicorn app.core.factory:create_app --factory --host 0.0.0.0 --port 8000 --reload

# AI Service setup (new terminal)
cd ai-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Optional: Add OPENAI_API_KEY=your_key_here to .env
python -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 4. Verification
- [ ] Backend running: http://localhost:8000/docs
- [ ] AI Service running: http://localhost:8001/docs  
- [ ] Frontend running: http://localhost:5173
- [ ] Database connected (check backend logs)
- [ ] Login works: admin@agenttwinops.dev / AdminPass123!@#

### 5. Feature Testing
- [ ] Infrastructure page loads
- [ ] Prediction functionality works
- [ ] Simulation functionality works
- [ ] Recommendations functionality works
- [ ] AI Service connects to backend successfully

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL status
pg_ctl status

# Verify database exists
psql -l | grep agenttwinops

# Check connection string in backend/.env
```

**AI Service Errors**
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check AI service logs for connection errors
```

**Frontend Build Errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📋 Environment Variables Summary

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5432/agenttwinops
SECRET_KEY=your_production_secret_key
APP_ENV=development
```

### AI Service (.env)  
```
BACKEND_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_key_here  # Optional
AI_SERVICE_MODE=real
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_API_BASE_URL=http://localhost:8001
VITE_ENABLE_MOCK_AI=false
```

## 🚀 Production Notes

- Change all passwords and secret keys
- Use proper SSL certificates
- Configure production database
- Set APP_ENV=production
- Review CORS origins for production domains
- Enable proper logging and monitoring

---

**Ready for deployment!** 🎉