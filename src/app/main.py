# src/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="Health Model Demo")

MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.pkl")
model = None

# Accept features as a dictionary
class InputData(BaseModel):
    features: dict   # keys = feature names, values = numeric

@app.on_event("startup")
def load_model():
    global model
    try:
        model = joblib.load(MODEL_PATH)
        print("Model loaded at", MODEL_PATH)
    except Exception as e:
        print("Could not load model:", e)
        model = None

@app.post("/predict")
def predict(payload: InputData):
    if model is None:
        return {"error": "model not loaded"}

    # Extract dict
    feature_dict = payload.features

    # Convert to DataFrame
    df = pd.DataFrame([feature_dict])

    # Predict
    pred = model.predict(df)[0]

    return {"prediction": int(pred)}
