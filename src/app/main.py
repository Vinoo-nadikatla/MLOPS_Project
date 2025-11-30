# src/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="Health Model Demo")

MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.pkl")
model = None

class InputData(BaseModel):
    features: list  # list of numeric features in same order used in training

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
    df = pd.DataFrame([payload.features])
    pred = model.predict(df)
    return {"prediction": pred.tolist()}
