#!/usr/bin/env powershell
# Start FastAPI Server Script

Write-Host "Starting Two-Stage ML API Server..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"

Write-Host "Model Path: $env:MODEL_PATH" -ForegroundColor Cyan
Write-Host "Config Path: $env:CONFIG_PATH" -ForegroundColor Cyan

.venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000

# Keep the window open
Write-Host "`nServer stopped. Press Enter to exit..." -ForegroundColor Yellow
Read-Host
