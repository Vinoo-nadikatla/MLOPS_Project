#!/usr/bin/env pwsh
# Helper: start the app locally (PowerShell)

# create venv if missing
if (-not (Test-Path -Path .venv)) {
    python -m venv .venv
}

# activate
. .venv\Scripts\Activate.ps1

# install deps
pip install --upgrade pip
pip install -r requirements.txt

# set MODEL_PATH if model exists in src/models
$modelPathTest = ".\src\models\model.pkl"
if (Test-Path $modelPathTest) {
    $modelPath = Resolve-Path $modelPathTest
    $env:MODEL_PATH = $modelPath.Path
    Write-Host "Using model at $($env:MODEL_PATH)"
} else {
    Write-Host "No model found at $modelPathTest. Please set MODEL_PATH environment variable manually if you want to use a specific model."
}

# run uvicorn
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
