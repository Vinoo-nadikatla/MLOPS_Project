# API Fields Documentation

## All Available Input Fields

The Two-Stage ML API accepts **13 fields** for each prediction sample. All fields are numeric (float).

### Field Definitions

| # | Field | Type | Description | Example Range |
|---|-------|------|-------------|---|
| 1 | **age** | float | Patient age in years | 29 - 77 |
| 2 | **sex** | float | Gender (1=Male, 0=Female) | 0.0 or 1.0 |
| 3 | **cp** | float | Chest pain type (0-3) | 0.0, 1.0, 2.0, 3.0 |
| 4 | **trestbps** | float | Resting blood pressure (mmHg) | 90 - 200 |
| 5 | **chol** | float | Serum cholesterol (mg/dl) | 126 - 564 |
| 6 | **fbs** | float | Fasting blood sugar > 120 (1=Yes, 0=No) | 0.0 or 1.0 |
| 7 | **restecg** | float | Resting ECG results (0-2) | 0.0, 1.0, 2.0 |
| 8 | **thalach** | float | Max heart rate achieved | 60 - 202 |
| 9 | **exang** | float | Exercise induced angina (1=Yes, 0=No) | 0.0 or 1.0 |
| 10 | **oldpeak** | float | ST depression induced by exercise | 0.0 - 6.2 |
| 11 | **slope** | float | ST segment slope (0-2) | 0.0, 1.0, 2.0 |
| 12 | **ca** | float | Number of major vessels (0-3) | 0.0, 1.0, 2.0, 3.0 |
| 13 | **thal** | float | Thalassemia type (0-3) | 0.0, 1.0, 2.0, 3.0 |

## API Endpoints

### 1. Single Prediction (Accepts ALL 13 fields)

**Endpoint:** `POST /predict`

**Request Body:**
```json
{
  "age": 45.0,
  "sex": 1.0,
  "cp": 3.0,
  "trestbps": 130.0,
  "chol": 250.0,
  "fbs": 0.0,
  "restecg": 1.0,
  "thalach": 150.0,
  "exang": 0.0,
  "oldpeak": 2.6,
  "slope": 0.0,
  "ca": 0.0,
  "thal": 0.0
}
```

**Response:**
```json
{
  "stage": "Stage 1: Random Forest Prediction",
  "prediction": 1,
  "probability": 0.76,
  "confidence": 0.76,
  "model_type": "RandomForestClassifier"
}
```

---

### 2. Batch Predictions (Accepts ALL 13 fields per sample)

**Endpoint:** `POST /batch_predict`

**Request Body:**
```json
{
  "samples": [
    {
      "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
      "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
      "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
    },
    {
      "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
      "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
      "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
    }
  ]
}
```

**Response:**
```json
{
  "stage": "Batch Predictions (Stage 1 only)",
  "n_predictions": 2,
  "predictions": [1, 0],
  "probabilities": [0.76, 0.28]
}
```

---

### 3. Two-Stage Pipeline (RF + Hungarian) - Accepts ALL 13 fields

**Endpoint:** `POST /predict_and_assign`

**Request Body:**
```json
{
  "samples": [
    {
      "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
      "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
      "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
    },
    {
      "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
      "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
      "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
    }
  ],
  "n_tasks": 2,
  "maximize_assignment": true
}
```

**Response:**
```json
{
  "stage": "Two-Stage Pipeline",
  "stage_1_rf_predictions": [1, 0],
  "stage_1_probabilities": [0.76, 0.28],
  "n_samples_processed": 2,
  "stage_2_optimal_assignments": [[0, 0], [1, 1]],
  "stage_2_total_score": 1.04,
  "assignment_explanation": "Each tuple (worker_idx, task_idx) represents optimal assignment"
}
```

---

## PowerShell Examples (Test ALL fields)

### Test 1: Single Prediction with ALL 13 fields

```powershell
$sample = @{
    age = 45.0
    sex = 1.0
    cp = 3.0
    trestbps = 130.0
    chol = 250.0
    fbs = 0.0
    restecg = 1.0
    thalach = 150.0
    exang = 0.0
    oldpeak = 2.6
    slope = 0.0
    ca = 0.0
    thal = 0.0
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $sample | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

### Test 2: Batch with different patient data

```powershell
$batch = @{
    samples = @(
        @{
            age = 45.0; sex = 1.0; cp = 3.0; trestbps = 130.0
            chol = 250.0; fbs = 0.0; restecg = 1.0; thalach = 150.0
            exang = 0.0; oldpeak = 2.6; slope = 0.0; ca = 0.0; thal = 0.0
        },
        @{
            age = 55.0; sex = 0.0; cp = 0.0; trestbps = 120.0
            chol = 200.0; fbs = 0.0; restecg = 0.0; thalach = 110.0
            exang = 0.0; oldpeak = 0.0; slope = 0.0; ca = 0.0; thal = 0.0
        },
        @{
            age = 50.0; sex = 1.0; cp = 2.0; trestbps = 140.0
            chol = 280.0; fbs = 1.0; restecg = 2.0; thalach = 140.0
            exang = 1.0; oldpeak = 4.2; slope = 2.0; ca = 3.0; thal = 3.0
        }
    )
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "http://localhost:8000/batch_predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $batch | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

### Test 3: Two-Stage Pipeline (Stage 1 + Stage 2)

```powershell
$pipeline = @{
    samples = @(
        @{
            age = 45.0; sex = 1.0; cp = 3.0; trestbps = 130.0
            chol = 250.0; fbs = 0.0; restecg = 1.0; thalach = 150.0
            exang = 0.0; oldpeak = 2.6; slope = 0.0; ca = 0.0; thal = 0.0
        },
        @{
            age = 55.0; sex = 0.0; cp = 0.0; trestbps = 120.0
            chol = 200.0; fbs = 0.0; restecg = 0.0; thalach = 110.0
            exang = 0.0; oldpeak = 0.0; slope = 0.0; ca = 0.0; thal = 0.0
        },
        @{
            age = 50.0; sex = 1.0; cp = 2.0; trestbps = 140.0
            chol = 280.0; fbs = 1.0; restecg = 2.0; thalach = 140.0
            exang = 1.0; oldpeak = 4.2; slope = 2.0; ca = 3.0; thal = 3.0
        }
    )
    n_tasks = 3
    maximize_assignment = $true
} | ConvertTo-Json -Depth 5

Invoke-WebRequest -Uri "http://localhost:8000/predict_and_assign" `
    -Method Post `
    -ContentType "application/json" `
    -Body $pipeline | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

---

## Python Examples (All fields testable)

### Test Single Prediction

```python
import requests
import json

url = "http://localhost:8000/predict"

# Enter data for ALL 13 fields
sample = {
    "age": 45.0,
    "sex": 1.0,
    "cp": 3.0,
    "trestbps": 130.0,
    "chol": 250.0,
    "fbs": 0.0,
    "restecg": 1.0,
    "thalach": 150.0,
    "exang": 0.0,
    "oldpeak": 2.6,
    "slope": 0.0,
    "ca": 0.0,
    "thal": 0.0
}

response = requests.post(url, json=sample)
print(json.dumps(response.json(), indent=2))
```

### Test Batch Predictions

```python
import requests
import json

url = "http://localhost:8000/batch_predict"

batch = {
    "samples": [
        {
            "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
            "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
            "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
        },
        {
            "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
            "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
            "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
        }
    ]
}

response = requests.post(url, json=batch)
print(json.dumps(response.json(), indent=2))
```

### Test Two-Stage Pipeline

```python
import requests
import json

url = "http://localhost:8000/predict_and_assign"

pipeline_data = {
    "samples": [
        {
            "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
            "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
            "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
        },
        {
            "age": 55.0, "sex": 0.0, "cp": 0.0, "trestbps": 120.0,
            "chol": 200.0, "fbs": 0.0, "restecg": 0.0, "thalach": 110.0,
            "exang": 0.0, "oldpeak": 0.0, "slope": 0.0, "ca": 0.0, "thal": 0.0
        },
        {
            "age": 50.0, "sex": 1.0, "cp": 2.0, "trestbps": 140.0,
            "chol": 280.0, "fbs": 1.0, "restecg": 2.0, "thalach": 140.0,
            "exang": 1.0, "oldpeak": 4.2, "slope": 2.0, "ca": 3.0, "thal": 3.0
        }
    ],
    "n_tasks": 3,
    "maximize_assignment": True
}

response = requests.post(url, json=pipeline_data)
result = response.json()

print("Stage 1 (Random Forest) Predictions:", result['stage_1_rf_predictions'])
print("Stage 1 Probabilities:", result['stage_1_probabilities'])
print("Stage 2 (Hungarian) Assignments:", result['stage_2_optimal_assignments'])
print("Total Assignment Score:", result['stage_2_total_score'])
```

---

## Field Value Ranges & Constraints

### Binary Fields (0 or 1)
- **sex**: 0.0 (Female), 1.0 (Male)
- **fbs**: 0.0 (No), 1.0 (Yes)
- **exang**: 0.0 (No), 1.0 (Yes)

### Categorical Fields (0-3)
- **cp** (Chest Pain): 0, 1, 2, 3
- **restecg** (Resting ECG): 0, 1, 2
- **slope** (ST Slope): 0, 1, 2
- **ca** (Vessels): 0, 1, 2, 3
- **thal** (Thalassemia): 0, 1, 2, 3

### Continuous Numeric Fields
- **age**: 29-77 years
- **trestbps**: 90-200 mmHg
- **chol**: 126-564 mg/dl
- **thalach**: 60-202 bpm
- **oldpeak**: 0.0-6.2 (ST depression)

---

## Summary

✅ **YES, the API accepts all 13 fields for data entry!**

- **Single Prediction**: 13 required fields
- **Batch Prediction**: Multiple samples, each with 13 fields
- **Two-Stage Pipeline**: Multiple samples with 13 fields + assignment parameters
- **All fields are required** (no optional fields)
- **All fields must be numeric** (float type)

---

**Last Updated**: December 3, 2025
