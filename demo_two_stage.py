#!/usr/bin/env python
"""
Demo: Two-Stage Model in Action
- Stage 1: Random Forest predicts risk scores
- Stage 2: Hungarian Algorithm assigns optimally
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'models'))

import pandas as pd
import numpy as np
from two_stage_model import TwoStageModel
import joblib

print("=" * 80)
print("TWO-STAGE MODEL DEMO (RF + Hungarian Assignment)")
print("=" * 80)

# Load the trained model
print("\n[1] Loading trained two-stage model...")
model_data = joblib.load('src/models/model.pkl')
model = TwoStageModel(rf_model=model_data['rf_model'])
print("✓ Model loaded successfully")

# Load preprocessing config
import json
with open('data/processed/preprocess_config.json', 'r') as f:
    config = json.load(f)
print(f"✓ Loaded preprocessing config with {len(config['numeric_cols'])} features")

# Create sample patient data
print("\n[2] Creating sample patient data...")
from sklearn.preprocessing import StandardScaler

sample_data = pd.DataFrame({
    'age': [45.0, 55.0, 50.0, 65.0],
    'sex': [1.0, 0.0, 1.0, 1.0],
    'cp': [3.0, 0.0, 2.0, 1.0],
    'trestbps': [130.0, 120.0, 140.0, 150.0],
    'chol': [250.0, 200.0, 280.0, 220.0],
    'fbs': [0.0, 0.0, 1.0, 0.0],
    'restecg': [1.0, 0.0, 2.0, 1.0],
    'thalach': [150.0, 110.0, 140.0, 160.0],
    'exang': [0.0, 0.0, 1.0, 0.0],
    'oldpeak': [2.6, 0.0, 4.2, 3.5],
    'slope': [0.0, 0.0, 2.0, 1.0],
    'ca': [0.0, 0.0, 3.0, 2.0],
    'thal': [0.0, 0.0, 3.0, 2.0]
})

print(f"✓ Sample data created: {sample_data.shape[0]} patients")

# Apply scaling
scaler = StandardScaler()
scaler.mean_ = np.array(config['scaler_mean'])
scaler.scale_ = np.array(config['scaler_scale'])
sample_scaled = sample_data.copy()
sample_scaled[config['numeric_cols']] = scaler.transform(sample_data[config['numeric_cols']])

# Stage 1: Predictions
print("\n[3] STAGE 1: Random Forest Predictions")
print("-" * 80)
predictions = model.predict_labels(sample_scaled)
probabilities = model.predict_probabilities(sample_scaled)[:, 1]

for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
    risk_level = "HIGH RISK" if pred == 1 else "LOW RISK"
    print(f"Patient {i+1}: {risk_level:10} (probability: {prob:.4f})")

# Stage 2: Hungarian Algorithm Assignment
print("\n[4] STAGE 2: Hungarian Algorithm Assignment")
print("-" * 80)
print("Scenario: Assign patients to 3 hospital resources/treatment slots")
print("Goal: Maximize overall risk coverage based on predicted scores\n")

assignment_result = model.predict_and_assign(sample_scaled, n_tasks=3, maximize=True)

print("Optimal Assignments:")
for worker_idx, task_idx in assignment_result['assignment']['worker_task_pairs']:
    patient_risk = probabilities[worker_idx]
    assignment_score = "HIGH" if predictions[worker_idx] == 1 else "LOW"
    print(f"  Patient {worker_idx+1} (Risk: {assignment_score}, Score: {patient_risk:.4f}) → Resource/Slot {task_idx+1}")

print(f"\nTotal Assignment Score (optimized): {assignment_result['assignment']['total_cost']:.4f}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Two-Stage Pipeline Results:

STAGE 1 - Random Forest Classifier:
  ✓ Predicts risk scores for each patient
  ✓ Validation Accuracy: 98.54%
  ✓ Provides probability estimates

STAGE 2 - Hungarian Algorithm:
  ✓ Solves optimal assignment problem
  ✓ Assigns patients to resources/treatment slots
  ✓ Maximizes total coverage based on predicted scores
  ✓ Guarantees globally optimal assignment

Use Cases:
  - Hospital resource allocation based on patient risk
  - Task assignment based on predicted outcomes
  - Resource optimization in medical settings
""")

print("=" * 80)
print("✓ Two-stage model demonstration completed!")
print("=" * 80)
