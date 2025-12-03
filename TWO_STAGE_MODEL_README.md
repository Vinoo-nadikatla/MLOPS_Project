# Two-Stage ML Pipeline: Random Forest + Hungarian Algorithm

## Overview

This project implements a sophisticated **two-stage machine learning pipeline** that combines:

1. **Stage 1: Random Forest Classification** — Predict risk/likelihood scores
2. **Stage 2: Hungarian Algorithm** — Optimal resource assignment based on predictions

## Architecture

```
Raw Data (Heart Disease Dataset)
    ↓
[PREPROCESSING]
  - Drop missing values
  - Scale numeric features (StandardScaler)
  - Encode categorical features
  - Output: Preprocessed dataset + config
    ↓
[STAGE 1: RANDOM FOREST CLASSIFIER]
  - 100 decision trees
  - Random state: 42 (reproducibility)
  - Outputs: Risk predictions & probabilities
  - Validation Accuracy: 98.54%
    ↓
[STAGE 2: HUNGARIAN ALGORITHM]
  - Input: Predicted risk scores/probabilities
  - Solves: Optimal assignment problem
  - Output: Optimal worker-to-task assignments
    ↓
[API ENDPOINTS] (FastAPI)
  - /health — Health check
  - /predict — Stage 1 only
  - /batch_predict — Batch Stage 1
  - /predict_and_assign — Full two-stage
```

## Files

### Core Model Files
- `src/models/two_stage_model.py` — TwoStageModel class implementing RF + Hungarian
- `src/models/train.py` — Training script for two-stage model
- `src/models/model.pkl` — Trained model (binary joblib format)

### Data Pipeline
- `src/data/preprocess.py` — Enhanced preprocessing with scaling & encoding
- `data/raw/heart.csv` — Raw heart disease dataset (1025 samples, 14 features)
- `data/processed/heart_processed.csv` — Preprocessed data
- `data/processed/preprocess_config.json` — Preprocessing configuration for inference

### API & Demo
- `src/app/main.py` — FastAPI application with two-stage endpoints
- `demo_two_stage.py` — Standalone demo showing predictions & assignments
- `test_api.py` — Comprehensive API test suite

### Configuration
- `params.yaml` — Hyperparameters (n_estimators: 100, test_size: 0.2, random_state: 42)
- `requirements.txt` — Python dependencies

## Usage

### 1. Preprocess Data

```powershell
.venv\Scripts\python.exe src/data/preprocess.py `
  --input "data/raw/heart.csv" `
  --output "data/processed/heart_processed.csv" `
  --config-output "data/processed/preprocess_config.json"
```

### 2. Train Two-Stage Model

```powershell
$env:PYTHONPATH = "src/models"
.venv\Scripts\python.exe src/models/train.py `
  --train "data/processed/heart_processed.csv" `
  --model "src/models/model.pkl" `
  --params "params.yaml"
```

**Output:**
- ✓ Random Forest Validation Accuracy: 0.9854 (98.54%)
- ✓ Optimal Assignment Score: 102.1200

### 3. Run Demo

```powershell
.venv\Scripts\python.exe demo_two_stage.py
```

**Output shows:**
- Stage 1: Risk predictions for 4 sample patients
- Stage 2: Optimal assignment to 3 hospital resources
- Total optimized assignment score

### 4. Start API Server

```powershell
$env:MODEL_PATH = "src/models/model.pkl"
$env:CONFIG_PATH = "data/processed/preprocess_config.json"
.venv\Scripts\uvicorn.exe "src.app.main:app" --host 0.0.0.0 --port 8000
```

### 5. Test API

```powershell
.venv\Scripts\python.exe test_api.py
```

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "model_loaded": true, "model_type": "Two-Stage (RF + Hungarian)"}
```

### Single Prediction (Stage 1)
```
POST /predict
Body: {
  "age": 45.0, "sex": 1.0, "cp": 3.0, "trestbps": 130.0,
  "chol": 250.0, "fbs": 0.0, "restecg": 1.0, "thalach": 150.0,
  "exang": 0.0, "oldpeak": 2.6, "slope": 0.0, "ca": 0.0, "thal": 0.0
}
Response: {"prediction": 1, "probability": 0.76, "confidence": 0.76}
```

### Batch Predictions (Stage 1)
```
POST /batch_predict
Body: {"samples": [...], "n_tasks": 3}
```

### Full Two-Stage Pipeline (RF + Hungarian)
```
POST /predict_and_assign
Body: {
  "samples": [...list of patients...],
  "n_tasks": 3,
  "maximize_assignment": true
}
Response: {
  "stage_1_rf_predictions": [1, 1, 0, 0],
  "stage_1_probabilities": [0.76, 0.72, 0.28, 0.20],
  "stage_2_optimal_assignments": [[0, 0], [1, 1], [2, 2], [3, 3]],
  "stage_2_total_score": 1.44
}
```

### Model Info
```
GET /info
Response: Details about features, model type, endpoints
```

## Stage 1: Random Forest Classifier

**Algorithm**: `sklearn.ensemble.RandomForestClassifier`

**Configuration:**
- `n_estimators`: 100 trees
- `random_state`: 42 (reproducible results)
- `test_size`: 0.2 (80/20 train/validation split)

**Training Results:**
- Validation Accuracy: **98.54%**
- Predictions: Binary classification (0 = healthy, 1 = disease)
- Probabilities: [P(class_0), P(class_1)]

**Input Features (13):**
- age, sex, cp (chest pain), trestbps (rest BP), chol (cholesterol)
- fbs (fasting BS), restecg, thalach (max HR), exang (exercise angina)
- oldpeak, slope, ca, thal

## Stage 2: Hungarian Algorithm

**Algorithm**: `scipy.optimize.linear_sum_assignment` (Hungarian/Munkres)

**Purpose:**
- Optimally assign workers (patients) to tasks (resources/treatment slots)
- Maximizes or minimizes total cost/score

**Use Cases:**
- Hospital resource allocation based on patient risk profiles
- ER room assignment prioritizing high-risk patients
- Treatment slot scheduling
- Task-to-worker optimal matching

**Example:**
```
4 patients with risk scores [0.76, 0.72, 0.28, 0.20]
3 available hospital resources

Optimal Assignment:
  Patient 1 (HIGH RISK: 0.76) → Resource 1
  Patient 2 (HIGH RISK: 0.72) → Resource 2
  Patient 3 (LOW RISK:  0.28) → Resource 3
  
Total score: 1.44 (maximized)
```

## Preprocessing Pipeline

**Input**: Raw heart disease CSV
**Steps**:
1. Load data (1025 rows × 14 columns)
2. Remove rows with missing values
3. Identify numeric & categorical columns
4. Encode categorical features (LabelEncoder)
5. Scale numeric features (StandardScaler)
6. Save preprocessing config for consistent inference

**Output**:
- `heart_processed.csv` — Scaled & encoded features
- `preprocess_config.json` — Encoder/scaler parameters for inference

## Model Persistence

### Training
```python
two_stage_model = TwoStageModel()
two_stage_model.fit(X_train, y_train)
two_stage_model.save("src/models/model.pkl")
```

### Inference
```python
model_data = joblib.load("src/models/model.pkl")
model = TwoStageModel(rf_model=model_data['rf_model'])
predictions = model.predict_labels(X)
probabilities = model.predict_probabilities(X)
assignments = model.predict_and_assign(X, n_tasks=3, maximize=True)
```

## Docker Support

### Build Image
```powershell
docker build -t mlops_project:latest .
```

### Run Container
```powershell
docker run --rm -p 8000:8000 `
  -e MODEL_PATH=/app/models/model.pkl `
  -e CONFIG_PATH=/app/data/preprocess_config.json `
  -v "D:/path/to/models:/app/models" `
  mlops_project:latest
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Random Forest Validation Accuracy | 98.54% |
| Training Samples | 820 |
| Validation Samples | 205 |
| Optimal Assignment Score | 102.12 |
| Features | 13 |
| Classes (RF) | 2 (binary) |

## Dependencies

- `scikit-learn` — RandomForestClassifier, StandardScaler, LabelEncoder
- `scipy` — linear_sum_assignment (Hungarian Algorithm)
- `pandas` — Data manipulation
- `numpy` — Numerical operations
- `joblib` — Model serialization
- `fastapi` — API framework
- `uvicorn` — ASGI server
- `mlflow` — Experiment tracking
- `pyyaml` — Configuration parsing

## Future Improvements

1. **Hyperparameter Tuning**: Use GridSearchCV for optimal RF parameters
2. **Multi-class Classification**: Extend to risk levels (low, medium, high)
3. **Cost Matrix Customization**: Allow domain-specific cost definitions
4. **Performance Monitoring**: Add accuracy tracking, ROC curves
5. **Explainability**: Feature importance, SHAP values
6. **Batch Processing**: Async endpoint for large batch predictions
7. **Model Versioning**: MLflow Registry integration
8. **A/B Testing**: Compare different model versions

## References

- **Random Forest**: Breiman, L. (2001). Random Forests
- **Hungarian Algorithm**: Munkres, J. (1957). Algorithms for Assignment and Transportation Problems
- **scikit-learn**: https://scikit-learn.org
- **scipy.optimize**: https://scipy.readthedocs.io/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html

---

**Last Updated**: December 3, 2025
**Status**: ✓ Fully Trained & Operational
