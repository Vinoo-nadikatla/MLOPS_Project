#!/usr/bin/env powershell
# MLOPS Project - Web Interface & API Server

Write-Host @"

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    Two-Stage ML Model - Web Interface & API Server     ║
║                                                          ║
║    Quick Start Guide                                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "src/models/model.pkl")) {
    Write-Host "ERROR: Model file not found at src/models/model.pkl" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "data/processed/preprocess_config.json")) {
    Write-Host "ERROR: Config file not found at data/processed/preprocess_config.json" -ForegroundColor Red
    exit 1
}

Write-Host "✓ All prerequisites found" -ForegroundColor Green

# Set environment
$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"

Write-Host @"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AVAILABLE OPTIONS:

1. API Server Only (Port 8000)
2. Web Server Only (Port 8080)
3. Both Servers (Recommended)
4. Exit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"@ -ForegroundColor White

$choice = Read-Host "Select option (1-4)"

function Start-APIServer {
    Write-Host "`n[API Server] Starting on http://127.0.0.1:8000..." -ForegroundColor Green
    Write-Host "[API Server] Press Ctrl+C to stop`n" -ForegroundColor Gray
    .venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000 --reload
}

function Start-WebServer {
    Write-Host "`n[Web Server] Starting on http://127.0.0.1:8080..." -ForegroundColor Green
    Write-Host "[Web Server] Press Ctrl+C to stop`n" -ForegroundColor Gray
    .venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1
}

switch ($choice) {
    "1" {
        Start-APIServer
    }
    "2" {
        Start-WebServer
    }
    "3" {
        Write-Host "`n[Setup] Killing any existing servers on ports 8000 & 8080..." -ForegroundColor Yellow
        Get-NetTCPConnection -LocalPort 8000, 8080 -ErrorAction SilentlyContinue | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
        
        # Start both in parallel
        Write-Host "`n[Setup] Starting both servers..." -ForegroundColor Yellow
        
        $apiJob = Start-Job -ScriptBlock {
            Set-Location D:\Brajesh\GitHubDsktop\MLOPS_Project
            $env:MODEL_PATH = "src/models/model.pkl"
            $env:CONFIG_PATH = "data/processed/preprocess_config.json"
            & .venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000 --reload
        } -Name "APIServer"
        
        Start-Sleep -Seconds 2
        
        $webJob = Start-Job -ScriptBlock {
            Set-Location D:\Brajesh\GitHubDsktop\MLOPS_Project
            & .venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1
        } -Name "WebServer"
        
        Start-Sleep -Seconds 2
        
        Write-Host @"

╔══════════════════════════════════════════════════════════╗
║                    SERVERS RUNNING                      ║
╚══════════════════════════════════════════════════════════╝

📍 API Server:        http://127.0.0.1:8000
📍 Web Interface:     http://127.0.0.1:8080/web_interface.html
📍 Swagger Docs:      http://127.0.0.1:8000/docs
📍 Health Check:      http://127.0.0.1:8000/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:

1. Open in browser: http://127.0.0.1:8080/web_interface.html
2. Click "Test Connection" button
3. Enter patient data and make predictions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONITOR SERVERS:

API Logs:     Receive-Job -Name APIServer -Keep
Web Logs:     Receive-Job -Name WebServer -Keep
Stop Both:    Stop-Job -Name APIServer, WebServer

Press Ctrl+C + Enter to stop, or close this window.

"@ -ForegroundColor Cyan
        
        # Keep the window open
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid option. Exiting..." -ForegroundColor Red
        exit 1
    }
}
