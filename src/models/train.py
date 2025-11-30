# src/models/train.py
import argparse
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import mlflow
import yaml
import os

def main(train, model, params):
    os.makedirs(os.path.dirname(model), exist_ok=True)
    with open(params) as f:
        p = yaml.safe_load(f)
    df = pd.read_csv(train)
    # a toy target: choose last numeric column assuming it exists
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=p['train']['test_size'], random_state=p['train']['random_state'])

    mlflow.set_experiment("health_experiment")
    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=p['train']['n_estimators'], random_state=p['train']['random_state'])
        clf.fit(X_train, y_train)
        acc = clf.score(X_val, y_val)
        mlflow.log_param("n_estimators", p['train']['n_estimators'])
        mlflow.log_metric("val_acc", float(acc))
        # save model locally
        joblib.dump(clf, model)
        mlflow.log_artifact(model)

    print(f"Model trained and saved to {model}. Val acc: {acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--params", required=True)
    args = parser.parse_args()
    main(args.train, args.model, args.params)
