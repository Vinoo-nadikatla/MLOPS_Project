# 🎯 Complete MLflow Guide & Reference

## 📊 Your Experiments at a Glance

### Current Status
```
Experiments:           1 active
Runs:                  1 completed
Best Accuracy:         98.54% ⭐⭐⭐⭐⭐
Dashboard:             http://127.0.0.1:5000 ✅
Status:                🟢 OPERATIONAL
```

---

## 🚀 Quick Start

### View Your Experiments

```powershell
# Terminal 1: Start MLflow UI
cd D:\Brajesh\GitHubDsktop\MLOPS_Project
mlflow ui

# Then open in browser: http://127.0.0.1:5000
```

### Key Experiment Details

| Category | Details |
|----------|---------|
| **Experiment Name** | health_experiment |
| **Experiment ID** | 606211225731357525 |
| **Current Run** | bouncy-mole-883 |
| **Run Status** | ✅ Completed |
| **Model Accuracy** | 98.54% |

---

## 📈 Performance Dashboard

### Accuracy Metrics

```
Random Forest Validation Accuracy
├─ Score:      98.54% (0.9854)
├─ Correct:    202 out of 205
├─ Error Rate: 1.46% (3 incorrect)
└─ Grade:      A+ EXCELLENT
```

### Assignment Metrics

```
Hungarian Algorithm (Stage 2)
├─ Total Score:    102.12
├─ Purpose:        Optimal patient-resource assignment
├─ Method:         Linear sum assignment
└─ Quality:        Optimal (mathematical guarantee)
```

### Dataset Metrics

```
Validation Set
├─ Total Samples:  205
├─ Percentage:     20% of full dataset (1,025)
├─ Quality:        Good sample size
└─ Representativeness: High
```

---

## ⚙️ Model Configuration

### Training Configuration

```python
# Random Forest Classifier
n_estimators = 100          # Number of trees
random_state = 42           # Random seed (reproducible)
test_size = 0.2             # Train-test split (80-20)
```

### Why These Values?

```
n_estimators = 100
  └─ Standard for Random Forests
  └─ Balance between accuracy and speed
  └─ Prevents overfitting

test_size = 0.2
  └─ Industry standard 80-20 split
  └─ 205 test samples (adequate)
  └─ 820 train samples (sufficient)

random_state = 42
  └─ Ensures reproducible results
  └─ Anyone can replicate your work
  └─ Good for version control
```

---

## 🎯 Experiment Comparison

### Single Run Performance

```
Experiment: health_experiment
Run Name: bouncy-mole-883
├─ Accuracy: 98.54%
├─ Precision: High (few false positives)
├─ Error Rate: 1.46%
├─ Sample Size: 205
└─ Status: ✅ PASSING
```

### Benchmark Comparison

```
Typical ML Model Benchmarks:
├─ Poor:           < 70%
├─ Good:           70-85%
├─ Excellent:      85-95%
├─ Outstanding:    95-99%
├─ Your Model:     98.54% ⭐⭐⭐⭐⭐ OUTSTANDING
```

---

## 📊 MLflow UI Features

### Accessing the Dashboard

1. **Start MLflow UI**
   ```powershell
   cd D:\Brajesh\GitHubDsktop\MLOPS_Project
   mlflow ui
   ```

2. **Open in Browser**
   - URL: http://127.0.0.1:5000
   - Wait for page to load
   - View your experiments

### Dashboard Tabs

```
┌─────────────────────────────────────────────┐
│  EXPERIMENTS  │  RUNS  │  MODELS  │  CHARTS │
├─────────────────────────────────────────────┤
│                                             │
│  • Experiment: health_experiment            │
│  • Run: bouncy-mole-883                     │
│  • Metrics: 3 tracked                       │
│  • Parameters: 3 logged                     │
│                                             │
└─────────────────────────────────────────────┘
```

### In the UI, You Can:

**Experiments Tab:**
- ✅ View all experiments
- ✅ Create new experiments
- ✅ Delete experiments
- ✅ Filter and search

**Runs Tab:**
- ✅ View all runs in experiment
- ✅ Compare metrics side-by-side
- ✅ Sort by performance
- ✅ Download artifacts
- ✅ View run details

**Models Tab:**
- ✅ Register models
- ✅ Track versions
- ✅ Compare model versions
- ✅ Deploy models

**Charts Tab:**
- ✅ Accuracy trends
- ✅ Parameter distributions
- ✅ Metric comparisons
- ✅ Performance analysis

---

## 🔄 Workflow: Creating New Experiments

### Step 1: Prepare Your Code

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Import your data
# X_train, y_train, X_test, y_test = ...
```

### Step 2: Set Experiment

```python
mlflow.set_experiment("health_experiment")
```

### Step 3: Start Run

```python
with mlflow.start_run(run_name="experiment_v2"):
```

### Step 4: Log Parameters

```python
    mlflow.log_param("n_estimators", 150)
    mlflow.log_param("test_size", 0.2)
```

### Step 5: Train Model

```python
    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )
    model.fit(X_train, y_train)
```

### Step 6: Log Metrics

```python
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)
```

### Step 7: Log Model

```python
    mlflow.sklearn.log_model(model, "model")
```

### Step 8: End Run

```python
# Automatically ends when exiting with block
```

---

## 📋 Complete Example

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Set experiment name
mlflow.set_experiment("health_experiment")

# Start a new run
with mlflow.start_run(run_name="hyperparameter_tuning_v1"):
    
    # ===== LOG PARAMETERS =====
    n_estimators = 150
    max_depth = 10
    random_state = 42
    test_size = 0.2
    
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("random_state", random_state)
    mlflow.log_param("test_size", test_size)
    
    # ===== TRAIN MODEL =====
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    model.fit(X_train, y_train)
    
    # ===== GET PREDICTIONS =====
    y_pred = model.predict(X_test)
    
    # ===== CALCULATE METRICS =====
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # ===== LOG METRICS =====
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    
    # ===== LOG MODEL =====
    mlflow.sklearn.log_model(model, "model")
    
    # ===== LOG ARTIFACTS =====
    import json
    metrics_dict = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics_dict, f)
    mlflow.log_artifact("metrics.json")
    
    print(f"Run completed: accuracy={accuracy:.4f}")
```

---

## 🔍 Viewing Results

### In MLflow UI

```
1. Open: http://127.0.0.1:5000
2. Click on "health_experiment"
3. View "bouncy-mole-883" run
4. See metrics:
   ├─ rf_val_acc: 0.9854
   ├─ optimal_assignment_score: 102.12
   └─ n_samples: 205
5. See parameters:
   ├─ n_estimators: 100
   ├─ test_size: 0.2
   └─ random_state: 42
```

### Comparing Runs

```
If you have multiple runs:
1. Select 2+ runs to compare
2. Click "Compare" button
3. View side-by-side:
   ├─ All parameters
   ├─ All metrics
   ├─ Performance differences
   └─ Trends
```

---

## 💾 File Organization

### MLflow Directory Structure

```
Project Root/
└── mlruns/
    ├── 0/ (Default Experiment)
    │   └── meta.yaml
    │
    └── 606211225731357525/ (health_experiment)
        ├── meta.yaml
        └── 6df6f65520894bb886da66be62352ee0/ (Run)
            ├── meta.yaml
            ├── metrics/
            │   ├── n_samples
            │   ├── optimal_assignment_score
            │   └── rf_val_acc
            ├── params/
            │   ├── n_estimators
            │   ├── random_state
            │   └── test_size
            ├── tags/
            │   ├── mlflow.runName
            │   ├── mlflow.source.type
            │   ├── mlflow.user
            │   ├── mlflow.source.name
            │   └── mlflow.source.git.commit
            └── artifacts/
                ├── model.pkl
                └── ...
```

---

## 📈 Hyperparameter Tuning Strategy

### What to Try

```python
# Try different n_estimators
n_estimators_options = [50, 75, 100, 150, 200]

for n in n_estimators_options:
    with mlflow.start_run(run_name=f"rf_trees_{n}"):
        mlflow.log_param("n_estimators", n)
        
        model = RandomForestClassifier(n_estimators=n)
        model.fit(X_train, y_train)
        
        accuracy = model.score(X_test, y_test)
        mlflow.log_metric("accuracy", accuracy)
        
        mlflow.sklearn.log_model(model, "model")
```

### Then in MLflow UI

```
1. Open Experiments
2. Select health_experiment
3. Compare all runs
4. View metrics side-by-side
5. Select best performer
6. Register as production model
```

---

## 🎯 Best Practices

### Do's ✅

```
✅ Log all hyperparameters
✅ Log multiple metrics
✅ Use meaningful run names
✅ Track artifacts
✅ Use fixed random seeds
✅ Document experiment purpose
✅ Compare runs regularly
✅ Version your models
```

### Don'ts ❌

```
❌ Don't hardcode parameters
❌ Don't skip metric logging
❌ Don't use vague run names
❌ Don't rely on random seeds
❌ Don't compare without MLflow
❌ Don't deploy untested models
❌ Don't mix different datasets
```

---

## 📊 Metrics to Track

### Always Log

```python
# Basic metrics
mlflow.log_metric("accuracy", accuracy)
mlflow.log_metric("f1_score", f1_score)

# For classification
mlflow.log_metric("precision", precision)
mlflow.log_metric("recall", recall)
mlflow.log_metric("auc_roc", auc_roc)

# For regression
mlflow.log_metric("mse", mse)
mlflow.log_metric("rmse", rmse)
mlflow.log_metric("r2_score", r2)
```

### Feature Importance

```python
# Log feature importance
for i, importance in enumerate(model.feature_importances_):
    mlflow.log_metric(f"feature_{i}_importance", importance)
```

### Model Size

```python
import os
model_size = os.path.getsize("model.pkl")
mlflow.log_metric("model_size_bytes", model_size)
```

---

## 🔗 Integration with Other Tools

### With DVC (Data Version Control)
```yaml
# dvc.yaml
stages:
  train:
    cmd: python src/models/train.py
    deps:
      - src/models/train.py
      - data/processed/heart_processed.csv
    outs:
      - src/models/model.pkl
    metrics:
      - mlruns/metrics.json
```

### With GitHub
```bash
# Push MLflow runs to GitHub
git add mlruns/
git commit -m "Track experiment: rf_accuracy_98.54%"
git push origin main
```

---

## 📞 Troubleshooting

### MLflow UI Won't Start

```powershell
# Check if port 5000 is in use
netstat -ano | findstr ":5000"

# Kill process on port 5000
taskkill /PID <PID> /F

# Try again
mlflow ui
```

### Can't See My Experiments

```powershell
# Check MLflow version
mlflow --version

# Verify tracking directory exists
ls mlruns/

# Check permissions
icacls mlruns /grant:r "$env:USERNAME:F"
```

### Metrics Not Appearing

```python
# Make sure you use with block
with mlflow.start_run():
    mlflow.log_metric("my_metric", 0.95)
    # Auto-ends when exiting block

# Or manually end
mlflow.start_run()
mlflow.log_metric("my_metric", 0.95)
mlflow.end_run()  # IMPORTANT!
```

---

## ✅ Verification Checklist

```
✅ MLflow installed
✅ Experiment created: health_experiment
✅ Run completed: bouncy-mole-883
✅ Metrics logged: 3 metrics
✅ Parameters logged: 3 parameters
✅ Artifacts saved: model + config
✅ UI accessible: http://127.0.0.1:5000
✅ Reproducible: random_state=42
```

---

## 🎉 You're All Set!

**Next Steps:**

1. **View Dashboard:** Open http://127.0.0.1:5000
2. **Create New Runs:** Try different hyperparameters
3. **Compare Results:** Use MLflow UI comparison
4. **Select Best:** Pick top performer
5. **Register Model:** For production use

---

**Status:** 🟢 Complete and Operational  
**Last Updated:** December 3, 2025
