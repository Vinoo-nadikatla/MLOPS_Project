# Web Interface Setup Guide

## ✅ Quick Start (Recommended)

### Option 1: Automated Setup (One Command)
```powershell
./start_all_servers.ps1
```

This will:
1. ✓ Start FastAPI server on port 8000
2. ✓ Start Web server on port 8080
3. ✓ Show you the URLs to open

Then open: **http://127.0.0.1:8080/web_interface.html**

---

## 📖 Manual Setup

### Step 1: Start FastAPI Server (Terminal 1)
```powershell
$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"
.venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
INFO:     Started server process [XXXX]
✓ Two-Stage Model loaded from src/models/model.pkl
✓ Preprocessing config loaded from data/processed/preprocess_config.json
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Web Server (Terminal 2)
```powershell
cd D:\Brajesh\GitHubDsktop\MLOPS_Project
.venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1
```

Expected output:
```
Serving HTTP on 127.0.0.1 port 8080
```

### Step 3: Open Web Interface
Open your browser and go to:
```
http://127.0.0.1:8080/web_interface.html
```

---

## 🧪 Test Connection

1. When the page loads, scroll to the top
2. Under **⚙️ Configuration**, click **"Test Connection"**
3. You should see: ✓ Connected! Model loaded: true

If connection fails:
- Ensure FastAPI server is running (check Terminal 1)
- Ensure Web server is running (check Terminal 2)
- Wait 2-3 seconds and try again

---

## 🎯 Using the Interface

### Tab 1: Single Prediction (Stage 1: Random Forest)
1. Fill in all 13 medical fields
2. Click "Predict"
3. View result: HIGH RISK 🔴 or LOW RISK 🟢

### Tab 2: Batch Predictions
1. Add multiple patients with "+ Add Another Patient"
2. Fill in data for each
3. Click "Predict All"
4. View results for all patients

### Tab 3: Two-Stage Pipeline
1. Set "Number of Tasks/Resources" (e.g., 3 hospital beds)
2. Set "Optimization" mode
3. Add patients with "+ Add Patient"
4. Click "Run Two-Stage Pipeline"
5. View:
   - Stage 1: RF predictions for each patient
   - Stage 2: Optimal assignments (Patient X → Resource Y)

### Tab 4: Model Info
1. Click "Get Model Info"
2. View model details and features

---

## 🔗 URLs Summary

| Purpose | URL |
|---------|-----|
| **Web Interface** | http://127.0.0.1:8080/web_interface.html |
| **API Base** | http://127.0.0.1:8000 |
| **API Swagger Docs** | http://127.0.0.1:8000/docs |
| **API ReDoc** | http://127.0.0.1:8000/redoc |
| **Health Check** | http://127.0.0.1:8000/health |

---

## 🛠️ Troubleshooting

### Issue: "Connection failed" in web interface

**Solution 1:** Wait a few seconds and click "Test Connection" again
- The servers might still be starting up

**Solution 2:** Verify both servers are running
```powershell
# Check port 8000 (FastAPI)
netstat -ano | findstr ":8000"

# Check port 8080 (Web server)
netstat -ano | findstr ":8080"
```

**Solution 3:** Kill and restart servers
```powershell
# Kill old processes
Get-Process python | Stop-Process -Force

# Restart servers
./start_all_servers.ps1
```

### Issue: "Model not loaded" error

**Causes:**
- Model file missing: `src/models/model.pkl`
- Config file missing: `data/processed/preprocess_config.json`
- Environment variables not set correctly

**Solution:**
1. Verify files exist:
   ```powershell
   ls src/models/model.pkl
   ls data/processed/preprocess_config.json
   ```

2. Check FastAPI console output for error messages
3. Restart servers with proper environment variables

### Issue: Port already in use

**Error:** "Address already in use"

**Solution:**
```powershell
# For port 8000
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F

# For port 8080
netstat -ano | findstr ":8080"
taskkill /PID <PID> /F

# Then restart servers
./start_all_servers.ps1
```

---

## 📊 API Endpoints Reference

### 1. Health Check
```
GET http://127.0.0.1:8000/health

Response:
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "Two-Stage (RF + Hungarian)",
  "config_loaded": true
}
```

### 2. Single Prediction (Stage 1)
```
POST http://127.0.0.1:8000/predict

Body: { 13 fields required }
Response: { prediction, probability, confidence }
```

### 3. Batch Predictions
```
POST http://127.0.0.1:8000/batch_predict

Body: { samples: [...], n_tasks: optional }
Response: { predictions: [...], probabilities: [...] }
```

### 4. Two-Stage Pipeline
```
POST http://127.0.0.1:8000/predict_and_assign

Body: { 
  samples: [...],
  n_tasks: 3,
  maximize_assignment: true
}

Response: {
  stage_1_rf_predictions: [...],
  stage_1_probabilities: [...],
  stage_2_optimal_assignments: [[patient_idx, task_idx], ...],
  stage_2_total_score: 102.12
}
```

### 5. Model Info
```
GET http://127.0.0.1:8000/info

Response: { model_type, feature_count, numeric_features: [...] }
```

---

## ✨ Features Implemented

✅ **CORS Enabled** - Web interface can communicate with API  
✅ **Real-time Status** - Loading indicators and error messages  
✅ **Beautiful UI** - Responsive design with gradient theme  
✅ **All 13 Fields** - Complete medical data input  
✅ **Batch Support** - Process multiple patients  
✅ **Two-Stage Visualization** - RF + Hungarian results  
✅ **Full API Documentation** - Swagger UI available  

---

## 🔍 Advanced: Running Tests

### Test with curl (PowerShell)
```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing | ConvertFrom-Json

# Single prediction
$data = @{
    age = 45
    sex = 1
    cp = 3
    trestbps = 130
    chol = 250
    fbs = 0
    restecg = 1
    thalach = 150
    exang = 0
    oldpeak = 2.6
    slope = 0
    ca = 0
    thal = 0
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/predict" `
    -Method POST `
    -ContentType "application/json" `
    -Body $data `
    -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json
```

---

## 📝 Notes

- The web interface works in all modern browsers (Chrome, Firefox, Edge, Safari)
- All data stays local - nothing is sent to external services
- The API uses FastAPI with automatic OpenAPI documentation
- You can access Swagger UI at: http://127.0.0.1:8000/docs
