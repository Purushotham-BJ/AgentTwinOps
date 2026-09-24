# AgentTwinOps Integration Test Script
Write-Host "=== AgentTwinOps Integration Test ===" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function RunTest {
    param([string]$name, [scriptblock]$block)
    Write-Host "TEST: $name" -ForegroundColor Yellow
    try {
        & $block
        Write-Host "  ✓ PASS`n" -ForegroundColor Green
        $script:passed++
    } catch {
        Write-Host "  ✗ FAIL: $($_.Exception.Message)`n" -ForegroundColor Red
        $script:failed++
    }
}

# Test 1: Backend Health
RunTest "Backend API Health" {
    $r = Invoke-RestMethod -Uri http://localhost:8000/api/v1/health
    Write-Host "  Backend: $($r.data.status), DB: $($r.data.database)"
}

# Test 2: AI Service Health
RunTest "AI Service Health" {
    $r = Invoke-RestMethod -Uri http://localhost:8001/api/v1/health
    Write-Host "  AI Service: $($r.status)"
}

# Test 3: CPU Prediction
RunTest "CPU Prediction" {
    $body = '{"service_id":"svc_001","horizon_minutes":60}'
    $r = Invoke-RestMethod -Method POST -Uri http://localhost:8001/api/v1/predict/cpu `
        -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "  Predicted: $($r.data.predicted_value)%, Risk: $($r.data.risk_level)"
}

# Test 4: Memory Prediction
RunTest "Memory Prediction" {
    $body = '{"service_id":"svc_002","horizon_minutes":120}'
    $r = Invoke-RestMethod -Method POST -Uri http://localhost:8001/api/v1/predict/memory `
        -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "  Predicted: $($r.data.predicted_value)%, Risk: $($r.data.risk_level)"
}

# Test 5: Digital Twins
RunTest "Digital Twins" {
    $r = Invoke-RestMethod -Uri http://localhost:8001/api/v1/twins
    Write-Host "  Total Twins: $($r.data.Count)"
    foreach ($twin in $r.data | Select-Object -First 3) {
        Write-Host "    - $($twin.name): Health=$([math]::Round($twin.health_score,1))%"
    }
}

# Test 6: Simulation
RunTest "Scenario Simulation" {
    $body = '{"scenario":"cpu_spike","service_id":"svc_001","parameters":{"spike_factor":2.0}}'
    $r = Invoke-RestMethod -Method POST -Uri http://localhost:8001/api/v1/simulate `
        -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "  Scenario: $($r.data.scenario)"
}

# Test 7: Recommendations
RunTest "AI Recommendations" {
    $r = Invoke-RestMethod -Uri http://localhost:8001/api/v1/recommendations
    Write-Host "  Total: $($r.data.Count)"
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total: $($passed + $failed), Passed: $passed, Failed: $failed"
if ($failed -eq 0) {
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
}
