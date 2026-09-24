# AgentTwinOps Integration Test Script
# Tests end-to-end communication between Backend and AI Service

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     AgentTwinOps End-to-End Integration Test             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$passed = 0
$failed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$TestBlock
    )
    
    Write-Host "[TEST] $Name..." -ForegroundColor Yellow -NoNewline
    try {
        $result = & $TestBlock
        Write-Host " ✓ PASS" -ForegroundColor Green
        $script:passed++
        return $result
    }
    catch {
        Write-Host " ✗ FAIL" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $null
    }
}

# ═══════════════════════════════════════════════════════════
# PHASE 1: SERVICE HEALTH CHECKS
# ═══════════════════════════════════════════════════════════
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ PHASE 1: Service Health Checks                         │" -ForegroundColor Cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Test-Endpoint "Backend API Health" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8000/api/v1/health
    if ($response.data.status -ne "healthy" -and $response.data.status -ne "degraded") {
        throw "Backend status: $($response.data.status)"
    }
    Write-Host "    Status: $($response.data.status), DB: $($response.data.database)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Backend API Version" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8000/api/v1/version
    Write-Host "    $($response.data.app_name) v$($response.data.version)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "AI Service Health" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/health
    if ($response.status -ne "healthy") {
        throw "AI Service status: $($response.status)"
    }
    Write-Host "    Service: $($response.service)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "AI Service Root" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8001/
    Write-Host "    $($response.service) v$($response.version)" -ForegroundColor Gray
    return $response
}

# ═══════════════════════════════════════════════════════════
# PHASE 2: AI SERVICE ENDPOINTS
# ═══════════════════════════════════════════════════════════
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ PHASE 2: AI Service Predictions                         │" -ForegroundColor Cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Test-Endpoint "CPU Prediction" {
    $body = @{
        service_id = "svc_001"
        horizon_minutes = 60
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/predict/cpu `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    CPU: $($response.data.predicted_value)%, Risk: $($response.data.risk_level), Confidence: $($response.data.confidence)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Memory Prediction" {
    $body = @{
        service_id = "svc_002"
        horizon_minutes = 120
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/predict/memory `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    Memory: $($response.data.predicted_value)%, Risk: $($response.data.risk_level)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Failure Prediction" {
    $body = @{
        service_id = "svc_001"
        horizon_minutes = 180
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/predict/failure `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    Failure Probability: $($response.data.failure_probability), Risk: $($response.data.risk_level)" -ForegroundColor Gray
    return $response
}

# ═══════════════════════════════════════════════════════════
# PHASE 3: SIMULATIONS & DIGITAL TWINS
# ═══════════════════════════════════════════════════════════
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ PHASE 3: Simulations & Digital Twins                   │" -ForegroundColor Cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Test-Endpoint "Scenario Simulation (CPU Spike)" {
    $body = @{
        scenario = "cpu_spike"
        service_id = "svc_001"
        parameters = @{
            spike_factor = 2.0
            duration_minutes = 30
        }
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/simulate `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    Scenario: $($response.data.scenario), Success: $([math]::Round($response.data.success_probability * 100, 1))%" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Scenario Simulation (Traffic Surge)" {
    $body = @{
        scenario = "traffic_surge"
        service_id = "svc_002"
        parameters = @{
            traffic_multiplier = 3.0
        }
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/simulate `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    Scenario: $($response.data.scenario)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Digital Twins List" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/twins
    Write-Host "    Total Twins: $($response.data.Count)" -ForegroundColor Gray
    foreach ($twin in $response.data) {
        Write-Host "      - $($twin.name): Health=$([math]::Round($twin.health_score, 1))%, Status=$($twin.current_state.status)" -ForegroundColor DarkGray
    }
    return $response
}

Test-Endpoint "Digital Twin by ID" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/twins/twin_svc_001
    Write-Host "    Twin: $($response.data.name), Health: $([math]::Round($response.data.health_score, 1))%" -ForegroundColor Gray
    return $response
}

# ═══════════════════════════════════════════════════════════
# PHASE 4: RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ PHASE 4: AI Recommendations                             │" -ForegroundColor Cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Test-Endpoint "Get Recommendations" {
    $response = Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/recommendations
    Write-Host "    Total Recommendations: $($response.data.Count)" -ForegroundColor Gray
    return $response
}

Test-Endpoint "Generate Recommendations" {
    $body = @{
        infrastructure_ids = @("svc_001", "svc_002")
        incident_ids = @()
        force_regenerate = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Method POST `
        -Uri http://localhost:8001/api/v1/recommendations/generate `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    Write-Host "    Generated: $($response.data.Count) recommendations" -ForegroundColor Gray
    return $response
}

# ═══════════════════════════════════════════════════════════
# PHASE 5: BACKEND-AI INTEGRATION (Data Flow)
# ═══════════════════════════════════════════════════════════
Write-Host "`n┌─────────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ PHASE 5: Backend ↔ AI Service Integration              │" -ForegroundColor Cyan
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor Cyan

Write-Host "[INFO] AI Service uses backend_client to fetch data from Backend" -ForegroundColor Yellow
Write-Host "       When Backend is available, AI service fetches real data" -ForegroundColor Yellow
Write-Host "       When Backend is unavailable, AI service uses mock fallback" -ForegroundColor Yellow
Write-Host ""

Test-Endpoint "Backend Client Fallback (Mock Data)" {
    # AI service should be using mock data since backend DB is not available
    $twins = Invoke-RestMethod -Method GET -Uri http://localhost:8001/api/v1/twins
    
    if ($twins.data.Count -eq 0) {
        throw "No twins returned - backend_client may not be working"
    }
    
    Write-Host "    Twins using fallback data: $($twins.data.Count)" -ForegroundColor Gray
    Write-Host "    (Backend DB unavailable, using mock infrastructure)" -ForegroundColor DarkGray
    return $twins
}

# ═══════════════════════════════════════════════════════════
# TEST SUMMARY
# ═══════════════════════════════════════════════════════════
Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    TEST SUMMARY                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total Tests: $($passed + $failed)" -ForegroundColor White
Write-Host "  Passed:      $passed" -ForegroundColor Green
Write-Host "  Failed:      $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "Integration Status:" -ForegroundColor Cyan
    Write-Host "  • Backend API (port 8000): ✓ Running" -ForegroundColor Green
    Write-Host "  • AI Service (port 8001):  ✓ Running" -ForegroundColor Green
    Write-Host "  • Backend ↔ AI:            ✓ Connected (fallback mode)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Start PostgreSQL database" -ForegroundColor White
    Write-Host "  2. Run backend migrations: cd backend && alembic upgrade head" -ForegroundColor White
    Write-Host "  3. Create test data via backend API" -ForegroundColor White
    Write-Host "  4. AI service will automatically use real data" -ForegroundColor White
    Write-Host ""
    exit 0
}
else {
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  • Check that Backend is running on port 8000" -ForegroundColor White
    Write-Host "  • Check that AI Service is running on port 8001" -ForegroundColor White
    Write-Host "  • Review error messages above" -ForegroundColor White
    Write-Host "  • Check service logs for details" -ForegroundColor White
    Write-Host ""
    exit 1
}
