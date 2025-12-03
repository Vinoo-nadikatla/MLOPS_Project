# How to Use the Web Interface

## Step 1: Start the API Server

### Option A: Using PowerShell Script (Recommended)
```powershell
./start_server.ps1
```

### Option B: Manual Command
```powershell
$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"
.venv\Scripts\uvicorn.exe src.app.main:app --host 127.0.0.1 --port 8000
```

The server should display:
```
INFO:     Started server process [XXXX]
✓ Two-Stage Model loaded from src/models/model.pkl
✓ Preprocessing config loaded from data/processed/preprocess_config.json
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Step 2: Open the Web Interface

1. Open `web_interface.html` in your web browser (Chrome, Firefox, Edge, Safari)
   - You can right-click the file and select "Open with" → your preferred browser
   - Or use: `start web_interface.html` in PowerShell

2. The interface should open showing 4 tabs:
   - Single Prediction
   - Batch Predictions
   - Two-Stage Pipeline
   - Model Info

## Step 3: Test the Connection

1. In the web interface, click the **"Test Connection"** button
   - It should show: ✓ Connected! Model loaded: true
   - If it fails, make sure the API server is running (Step 1)

## Step 4: Make Predictions

### Single Patient Prediction (Stage 1)
1. Go to "Single Prediction" tab
2. Fill in all 13 medical fields (default values are pre-filled)
3. Click "Predict"
4. View the result showing: prediction (HIGH/LOW RISK), probability, and confidence

### Batch Predictions
1. Go to "Batch Predictions" tab
2. Add multiple patients using "+ Add Another Patient" button
3. Fill in data for each patient
4. Click "Predict All"
5. View results for all patients

### Two-Stage Pipeline
1. Go to "Two-Stage Pipeline" tab
2. Configure:
   - Number of Tasks/Resources (1-10)
   - Optimization mode (Maximize or Minimize)
3. Add patients using "+ Add Patient" button
4. Click "Run Two-Stage Pipeline"
5. View results:
   - **Stage 1**: RF predictions for each patient
   - **Stage 2**: Optimal assignments from Hungarian Algorithm

## Troubleshooting

### "Connection failed" error
- ✓ Verify the API server is running (see Step 1)
- ✓ Check that port 8000 is not blocked by firewall
- ✓ Verify the API URL in the interface is correct (should be `http://localhost:8000`)
- ✓ Try waiting 2-3 seconds after starting the server before testing

### API returns "Model not loaded"
- ✓ Ensure `src/models/model.pkl` exists
- ✓ Ensure `data/processed/preprocess_config.json` exists
- ✓ Check the server console output for error messages
- ✓ Verify MODEL_PATH and CONFIG_PATH environment variables are set correctly

### Port 8000 already in use
```powershell
# Kill the process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
```

Then restart the server.

## API Endpoints Used

The web interface connects to these endpoints:

1. **GET /health**
   - Test connection and model status
   - No parameters

2. **POST /predict**
   - Single patient prediction (Stage 1: Random Forest)
   - Takes 13 medical fields as input

3. **POST /batch_predict**
   - Multiple patient predictions
   - Takes array of samples

4. **POST /predict_and_assign**
   - Full two-stage pipeline
   - Stage 1: RF predictions
   - Stage 2: Hungarian optimal assignment

5. **GET /info**
   - Model information and feature descriptions

## Input Fields (All 13 Required)

| Field | Type | Range | Example |
|-------|------|-------|---------|
| age | Number | 0-120 | 45 |
| sex | Select | 0=Female, 1=Male | 1 |
| cp | Select | 0-3 (Chest Pain Type) | 3 |
| trestbps | Number | 80-200 | 130 |
| chol | Number | 100-600 | 250 |
| fbs | Select | 0=<120, 1=>120 | 0 |
| restecg | Select | 0-2 (ECG) | 1 |
| thalach | Number | 60-210 | 150 |
| exang | Select | 0=No, 1=Yes | 0 |
| oldpeak | Number | 0-7 | 2.6 |
| slope | Select | 0-2 (ST Slope) | 0 |
| ca | Number | 0-3 | 0 |
| thal | Select | 0-3 (Thalassemia) | 0 |

## Features

✨ **Responsive Design** - Works on desktop, tablet, and mobile  
✨ **Real-time Status** - Loading indicators and error messages  
✨ **Beautiful UI** - Gradient design with organized sections  
✨ **Full API Support** - All endpoints accessible from one interface  
✨ **Batch Processing** - Add/remove samples dynamically  
✨ **Two-Stage Visualization** - Clear display of RF + Hungarian results
