# src/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd
import numpy as np
import os
import json
import sys
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Import two-stage model
# Add candidate paths so import works when app is placed at different locations
candidate_model_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'models'),  # src/app/../models
    os.path.join(os.path.dirname(__file__), 'models'),       # src/app/models
    os.path.join(os.getcwd(), 'src', 'models'),              # project-root/src/models
    os.path.join(os.getcwd(), 'models'),                     # project-root/models
    os.path.join(os.sep, 'app', 'models'),                  # /app/models (container common)
]

for p in candidate_model_paths:
    try:
        if p and os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)
    except Exception:
        # ignore any invalid path errors
        pass

try:
    from two_stage_model import TwoStageModel
except Exception:
    # Fallback to package import if available
    try:
        from src.models.two_stage_model import TwoStageModel
    except Exception:
        raise

app = FastAPI(title="Two-Stage Health Model API")

# Serve static files (web UI) from project root so container can serve the
# bundled `web_interface.html`. `main.py` lives at `src/app`, so go up two
# directories to reach repo root where `web_interface.html` is located.
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Mount static files at /static and serve the single-page UI at /
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def root():
    index_path = os.path.join(STATIC_DIR, 'web_interface.html')
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type='text/html')
    return {"message": "Web UI not found. Place 'web_interface.html' in project root or access /docs for API docs."}

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.environ.get("MODEL_PATH", "src/models/model.pkl")
CONFIG_PATH = os.environ.get("CONFIG_PATH", "data/processed/preprocess_config.json")

model = None
preprocess_config = None
scaler = None

# Input schema for prediction
class PredictionInput(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float

class BatchPredictionInput(BaseModel):
    """For batch predictions and assignments"""
    samples: List[PredictionInput]
    n_tasks: Optional[int] = None
    maximize_assignment: Optional[bool] = True

@app.on_event("startup")
def load_model_and_config():
    global model, preprocess_config, scaler
    try:
        # Load two-stage model
        model_data = joblib.load(MODEL_PATH)
        model = TwoStageModel(rf_model=model_data['rf_model'])
        print(f"✓ Two-Stage Model loaded from {MODEL_PATH}")
        
        # Load preprocessing config
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                preprocess_config = json.load(f)
            print(f"✓ Preprocessing config loaded from {CONFIG_PATH}")
            
            # Recreate scaler from config
            scaler = StandardScaler()
            scaler.mean_ = np.array(preprocess_config.get('scaler_mean', []))
            scaler.scale_ = np.array(preprocess_config.get('scaler_scale', []))
        else:
            print(f"⚠ Preprocessing config not found at {CONFIG_PATH}")
            
    except Exception as e:
        print(f"✗ Error loading model or config: {e}")
        model = None
        preprocess_config = None

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_type": "Two-Stage (RF + Hungarian)",
        "config_loaded": preprocess_config is not None
    }

@app.post("/predict")
def predict(data: PredictionInput):
    """Stage 1: Random Forest Prediction - predict risk/likelihood"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert input to DataFrame
        feature_dict = data.dict()
        df = pd.DataFrame([feature_dict])
        
        # Get numeric columns in correct order
        numeric_cols = preprocess_config.get('numeric_cols', df.columns.tolist()) if preprocess_config else df.columns.tolist()
        df = df[numeric_cols]
        
        # Apply scaling if config available
        if scaler is not None and preprocess_config:
            df_scaled = df.copy()
            df_scaled[numeric_cols] = scaler.transform(df[numeric_cols])
            df = df_scaled
        
        # Stage 1 prediction
        probs = model.predict_probabilities(df)
        prediction = int(model.predict_labels(df)[0])
        probability = float(probs[0, 1]) if probs.shape[1] > 1 else float(probs[0, 0])
        
        return {
            "stage": "Stage 1: Random Forest Prediction",
            "prediction": prediction,
            "probability": probability,
            "confidence": float(max(probs[0])),
            "model_type": "RandomForestClassifier"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/predict_and_assign")
def predict_and_assign(data: BatchPredictionInput):
    """
    Two-Stage Pipeline:
    Stage 1: Random Forest - predict likelihood scores for each sample
    Stage 2: Hungarian Algorithm - optimal assignment of samples to tasks
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert batch inputs to DataFrame
        records = [s.dict() for s in data.samples]
        df = pd.DataFrame(records)
        
        # Get numeric columns in correct order
        numeric_cols = preprocess_config.get('numeric_cols', df.columns.tolist()) if preprocess_config else df.columns.tolist()
        df = df[numeric_cols]
        
        # Apply scaling if config available
        if scaler is not None and preprocess_config:
            df_scaled = df.copy()
            df_scaled[numeric_cols] = scaler.transform(df[numeric_cols])
            df = df_scaled
        
        # Two-stage prediction and assignment
        result = model.predict_and_assign(
            df, 
            n_tasks=data.n_tasks or len(df),
            maximize=data.maximize_assignment if data.maximize_assignment is not None else True
        )
        
        return {
            "stage": "Two-Stage Pipeline",
            "stage_1_rf_predictions": result['predictions'],
            "stage_1_probabilities": result['probabilities'],
            "n_samples_processed": result['n_samples'],
            "stage_2_optimal_assignments": result['optimal_assignments'],
            "stage_2_total_score": result['total_assignment_score'],
            "assignment_explanation": "Each tuple (worker_idx, task_idx) represents optimal assignment"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction and assignment error: {str(e)}")

@app.post("/batch_predict")
def batch_predict(data: BatchPredictionInput):
    """Batch predictions using Random Forest only"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        records = [s.dict() for s in data.samples]
        df = pd.DataFrame(records)
        
        numeric_cols = preprocess_config.get('numeric_cols', df.columns.tolist()) if preprocess_config else df.columns.tolist()
        df = df[numeric_cols]
        
        if scaler is not None and preprocess_config:
            df_scaled = df.copy()
            df_scaled[numeric_cols] = scaler.transform(df[numeric_cols])
            df = df_scaled
        
        probs = model.predict_probabilities(df)
        predictions = model.predict_labels(df)
        
        return {
            "stage": "Batch Predictions (Stage 1 only)",
            "n_predictions": len(predictions),
            "predictions": predictions.tolist(),
            "probabilities": probs[:, 1].tolist() if probs.shape[1] > 1 else probs[:, 0].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")

@app.get("/info")
def model_info():
    """Get model and preprocessing information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "Two-Stage ML Pipeline",
        "stage_1": "Random Forest Classifier (100 estimators)",
        "stage_2": "Hungarian Algorithm (scipy.optimize.linear_sum_assignment)",
        "model_path": MODEL_PATH,
        "config_path": CONFIG_PATH,
        "numeric_features": preprocess_config.get('numeric_cols', []) if preprocess_config else [],
        "feature_count": len(preprocess_config.get('numeric_cols', [])) if preprocess_config else 0,
        "endpoints": {
            "/predict": "Single sample RF prediction (Stage 1 only)",
            "/batch_predict": "Batch RF predictions (Stage 1 only)",
            "/predict_and_assign": "Full two-stage pipeline with Hungarian assignment"
        }
    }


