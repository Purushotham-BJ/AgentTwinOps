# Start AI Service
Write-Host "🚀 Starting AgentTwinOps AI Service..." -ForegroundColor Cyan

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Start service
Write-Host "Starting AI service on port 8001..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8001 --host 0.0.0.0
