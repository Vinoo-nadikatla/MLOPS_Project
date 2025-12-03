# src/models/train.py
import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
import mlflow
import yaml
import os
from two_stage_model import TwoStageModel

def main(train, model, params):
    os.makedirs(os.path.dirname(model), exist_ok=True)
    with open(params) as f:
        p = yaml.safe_load(f)
    
    df = pd.read_csv(train)
    # Features are all columns except last (target)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    # Convert to DataFrame to preserve column names
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, 
        test_size=p['train']['test_size'], 
        random_state=p['train']['random_state']
    )

    mlflow.set_experiment("health_experiment")
    with mlflow.start_run():
        # Stage 1: Train Random Forest
        two_stage_model = TwoStageModel()
        two_stage_model.fit(X_train, y_train)
        
        # Validate Random Forest predictions
        rf_pred = two_stage_model.predict_labels(X_val)
        rf_acc = (rf_pred == y_val.values).mean()
        
        # Stage 2: Test Hungarian Assignment on validation set
        assignment_result = two_stage_model.predict_and_assign(X_val, maximize=True)
        
        # Log metrics
        mlflow.log_param("n_estimators", p['train']['n_estimators'])
        mlflow.log_param("test_size", p['train']['test_size'])
        mlflow.log_param("random_state", p['train']['random_state'])
        mlflow.log_metric("rf_val_acc", float(rf_acc))
        mlflow.log_metric("n_samples", len(X_val))
        mlflow.log_metric("optimal_assignment_score", assignment_result['total_assignment_score'])
        
        # Save model
        two_stage_model.save(model)
        mlflow.log_artifact(model)

    print(f"✓ Two-stage model trained and saved to {model}")
    print(f"  - Random Forest Validation Accuracy: {rf_acc:.4f}")
    print(f"  - Optimal Assignment Score: {assignment_result['total_assignment_score']:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True, help="Path to preprocessed training data")
    parser.add_argument("--model", required=True, help="Path to save model")
    parser.add_argument("--params", required=True, help="Path to params.yaml")
    args = parser.parse_args()
    main(args.train, args.model, args.params)
