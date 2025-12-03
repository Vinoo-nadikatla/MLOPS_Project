# 🚀 Web Interface - Complete Setup Guide

## Problem Solved ✅

**Issue:** Web interface opened via `file:///` couldn't connect to API  
**Root Cause:** CORS restrictions + improper serving  
**Solution:** CORS middleware + HTTP server for static files  

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Your Browser                          │
│                                                         │
│  http://127.0.0.1:8080/web_interface.html             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────────┐         ┌──────────────────┐
   │  HTTP Server│         │  FastAPI Server  │
   │  Port 8080  │         │  Port 8000       │
   │             │         │                  │
   │ Serves HTML │         │ ✅ CORS Enabled  │
   │ + CSS + JS  │         │ ML Model Loaded  │
   └─────────────┘         │ Config Loaded    │
                           └──────────────────┘
```

---

## 🎯 ONE COMMAND TO START

```powershell
./start_servers.ps1
```

Then choose option `3` (Both Servers)

**That's it!** Both servers will start automatically.

---

## 📍 Where to Go

After servers start, open your browser and go to:

```
http://127.0.0.1:8080/web_interface.html
```

---

## ✅ Verify It's Working

1. **Click the "Test Connection" button** (top of page under ⚙️ Configuration)
2. Should see: **✓ Connected! Model loaded: true**
3. Try a prediction on any tab

---

## 📋 Server Status Checklist

```
□ FastAPI Server running?    http://127.0.0.1:8000/health
□ Web Server running?         http://127.0.0.1:8080
□ Model loaded?               Check FastAPI console
□ Web interface accessible?   http://127.0.0.1:8080/web_interface.html
□ Connection test passing?    Click "Test Connection" button
```

---

## 🎨 Web Interface Tabs

### 📊 Tab 1: Single Prediction
```
Input:  13 medical fields (pre-filled with examples)
Output: HIGH RISK 🔴 or LOW RISK 🟢
        Probability: 87.5%
        Confidence: 94.2%
```

### 📋 Tab 2: Batch Predictions
```
Input:  Multiple patients
Output: Table with all predictions
        Option to add/remove patients
```

### 🔄 Tab 3: Two-Stage Pipeline
```
Input:  Patients + Number of resources
Output: Stage 1: RF predictions
        Stage 2: Optimal assignments (Patient X → Resource Y)
        Total score: 102.12
```

### ℹ️ Tab 4: Model Info
```
Output: Model type, features, architecture details
```

---

## 🛠️ Manual Server Start (If Needed)

### Terminal 1 - API Server
```powershell
cd D:\Brajesh\GitHubDsktop\MLOPS_Project

$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"

.venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
✓ Two-Stage Model loaded from src/models/model.pkl
✓ Preprocessing config loaded from data/processed/preprocess_config.json
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Web Server
```powershell
cd D:\Brajesh\GitHubDsktop\MLOPS_Project

.venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1
```

Expected output:
```
Serving HTTP on 127.0.0.1 port 8080 (http://127.0.0.1:8080/) ...
```

---

## 🌐 API URLs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if API is running |
| `/info` | GET | Get model information |
| `/predict` | POST | Single patient prediction |
| `/batch_predict` | POST | Multiple patient predictions |
| `/predict_and_assign` | POST | Two-stage pipeline |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

---

## 🔧 If Connection Fails

### Quick Checks
```powershell
# 1. Is FastAPI running on port 8000?
curl http://127.0.0.1:8000/health

# 2. Is Web server running on port 8080?
curl http://127.0.0.1:8080

# 3. Is the model file present?
ls src/models/model.pkl

# 4. Is config file present?
ls data/processed/preprocess_config.json
```

### Kill & Restart
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Wait 2 seconds
Start-Sleep -Seconds 2

# Restart servers
./start_servers.ps1
```

---

## 📊 13 Medical Input Fields

All fields are visible in the Single Prediction tab:

1. **Age** (0-120 years)
2. **Sex** (0=Female, 1=Male)
3. **Chest Pain Type** (0-3)
4. **Resting Blood Pressure** (mmHg)
5. **Cholesterol** (mg/dl)
6. **Fasting Blood Sugar** (0=<120, 1=>120)
7. **Resting ECG** (0-2)
8. **Max Heart Rate** (bpm)
9. **Exercise Angina** (0=No, 1=Yes)
10. **ST Depression** (0-7)
11. **ST Slope** (0=Up, 1=Flat, 2=Down)
12. **Major Vessels** (0-3)
13. **Thalassemia** (0-3)

All fields have default values and ranges set. Just fill them in and click Predict!

---

## 💾 Files Involved

```
✅ src/app/main.py
   └─ Updated with CORS middleware
   
✅ web_interface.html
   └─ Your web interface (already created)
   
✅ src/models/model.pkl
   └─ Trained two-stage model
   
✅ data/processed/preprocess_config.json
   └─ Feature scaling configuration
   
✅ start_servers.ps1
   └─ Easy startup with menu
```

---

## 🎯 Success Criteria

When everything is working:

✅ Browser shows web interface at: http://127.0.0.1:8080/web_interface.html
✅ "Test Connection" button returns: ✓ Connected! Model loaded: true
✅ Can enter patient data and get predictions
✅ Predictions show: HIGH RISK 🔴 or LOW RISK 🟢
✅ Batch and two-stage modes work without errors

---

## 📞 Last Resort Troubleshooting

If you've tried everything:

```powershell
# 1. Navigate to project directory
cd D:\Brajesh\GitHubDsktop\MLOPS_Project

# 2. Check Python environment
.venv\Scripts\python.exe --version

# 3. Check required files
ls src/models/model.pkl
ls data/processed/preprocess_config.json
ls web_interface.html

# 4. Test API can be imported
.venv\Scripts\python.exe -c "from src.app.main import app; print('OK')"

# 5. Start fresh
./start_servers.ps1
```

---

## 🎉 You're All Set!

1. Run: `./start_servers.ps1`
2. Open: `http://127.0.0.1:8080/web_interface.html`
3. Click: "Test Connection"
4. See: ✓ Connected!

**Happy predicting! 🚀**
