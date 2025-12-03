#!/usr/bin/env powershell
# Complete MLOps Project Server Startup Script

Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Two-Stage ML API - Complete Server Setup        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Kill any existing processes on ports 8000 and 8080
Write-Host "[1] Cleaning up existing servers..." -ForegroundColor Yellow
try {
    $proc8000 = Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -like "*python*"} | Where-Object {
        $ports = Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue
        $ports | Where-Object {$_.LocalPort -eq 8000}
    }
    if ($proc8000) {
        $proc8000 | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "    ✓ Cleaned port 8000" -ForegroundColor Green
    }
    
    $proc8080 = Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.ProcessName -like "*python*"} | Where-Object {
        $ports = Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue
        $ports | Where-Object {$_.LocalPort -eq 8080}
    }
    if ($proc8080) {
        $proc8080 | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "    ✓ Cleaned port 8080" -ForegroundColor Green
    }
} catch {
    Write-Host "    (No existing processes to clean)" -ForegroundColor Gray
}

# Set environment variables
Write-Host "`n[2] Configuring environment..." -ForegroundColor Yellow
$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"
Write-Host "    ✓ MODEL_PATH = $env:MODEL_PATH" -ForegroundColor Green
Write-Host "    ✓ CONFIG_PATH = $env:CONFIG_PATH" -ForegroundColor Green

# Start FastAPI server
Write-Host "`n[3] Starting FastAPI Server (Port 8000)..." -ForegroundColor Yellow
Start-Job -Name "FastAPI" -ScriptBlock {
    Set-Location D:\Brajesh\GitHubDsktop\MLOPS_Project
    $env:MODEL_PATH = "src/models/model.pkl"
    $env:CONFIG_PATH = "data/processed/preprocess_config.json"
    & .venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000 --reload
} | Out-Null

Write-Host "    ⏳ Waiting for FastAPI to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Start HTTP server for web interface
Write-Host "`n[4] Starting Web Server (Port 8080)..." -ForegroundColor Yellow
Start-Job -Name "WebServer" -ScriptBlock {
    Set-Location D:\Brajesh\GitHubDsktop\MLOPS_Project
    & .venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1
} | Out-Null

Write-Host "    ⏳ Waiting for Web Server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Verify both servers are running
Write-Host "`n[5] Verifying servers..." -ForegroundColor Yellow
$fastapi = Get-Job -Name "FastAPI" -ErrorAction SilentlyContinue
$webserver = Get-Job -Name "WebServer" -ErrorAction SilentlyContinue

if ($fastapi -and $fastapi.State -eq "Running") {
    Write-Host "    ✓ FastAPI is running" -ForegroundColor Green
} else {
    Write-Host "    ✗ FastAPI failed to start" -ForegroundColor Red
}

if ($webserver -and $webserver.State -eq "Running") {
    Write-Host "    ✓ Web Server is running" -ForegroundColor Green
} else {
    Write-Host "    ✗ Web Server failed to start" -ForegroundColor Red
}

Write-Host "`n" + "═" * 50 -ForegroundColor Cyan
Write-Host "🚀 SERVERS READY!" -ForegroundColor Green
Write-Host "═" * 50 -ForegroundColor Cyan

Write-Host "`n📋 URLS:" -ForegroundColor Yellow
Write-Host "  API Server:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Web Interface: http://127.0.0.1:8080/web_interface.html" -ForegroundColor White
Write-Host "`n📚 API Docs:" -ForegroundColor Yellow
Write-Host "  Swagger UI: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  ReDoc:      http://127.0.0.1:8000/redoc" -ForegroundColor White

Write-Host "`n📖 USAGE:" -ForegroundColor Yellow
Write-Host "  1. Open browser to: http://127.0.0.1:8080/web_interface.html" -ForegroundColor White
Write-Host "  2. Click 'Test Connection' to verify API is working" -ForegroundColor White
Write-Host "  3. Fill in patient data and make predictions" -ForegroundColor White

Write-Host "`n⚙️  MONITORING:" -ForegroundColor Yellow
Write-Host "  View FastAPI logs:  Receive-Job -Name FastAPI -Keep" -ForegroundColor Gray
Write-Host "  View Web logs:      Receive-Job -Name WebServer -Keep" -ForegroundColor Gray
Write-Host "  Stop servers:       Stop-Job -Name FastAPI, WebServer" -ForegroundColor Gray

Write-Host "`n" + "═" * 50 -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop or wait for updates...\n" -ForegroundColor Yellow

# Keep the window open and display live logs
while ($true) {
    Start-Sleep -Seconds 1
}
