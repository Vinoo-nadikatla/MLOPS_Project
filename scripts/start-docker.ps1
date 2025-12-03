#!/usr/bin/env pwsh
# Helper: build image and run container mounting local src/models

# build image
docker build -t mlops_project:latest .

# host models directory (adjust if your models live elsewhere)
if (Test-Path .\src\models) {
    $hostModels = (Resolve-Path .\src\models).Path
} else {
    Write-Host "Warning: ./src/models not found. If you want to mount a model, create it at src/models or edit this script."
    exit 1
}

# run container mounting the models folder
docker run --rm -p 8000:8000 `
  -e MODEL_PATH=/app/models/model.pkl `
  -v "${hostModels}:/app/models" `
  mlops_project:latest
