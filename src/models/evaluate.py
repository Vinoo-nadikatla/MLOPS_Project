# src/models/evaluate.py

import argparse
import joblib
import pandas as pd
import os
import mlflow
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, confusion_matrix, roc_curve, roc_auc_score,
    classification_report, precision_recall_curve, average_precision_score,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

def save_plot(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path, bbox_inches="tight")
    plt.close()

def main(model_path, test_path, report_path):

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # Load model from dictionary
    model_dict = joblib.load(model_path)
    model = model_dict["rf_model"]
    feature_names = model_dict["feature_names"]

    # Load test data
    df = pd.read_csv(test_path)
    X_test = df.iloc[:, :-1]
    y_test = df.iloc[:, -1]

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Basic metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    with open(report_path, "w") as f:
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(report)

    print(f"✓ Test Accuracy: {accuracy:.4f}")

    # ======== ROC Curve ==========
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    plt.figure(figsize=(5,4))
    plt.plot(fpr, tpr, label=f"AUC={auc:.3f}")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    roc_path = "reports/metrics/roc_curve.png"
    save_plot(roc_path)

    # ======== Precision Recall Curve ==========
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)

    plt.figure(figsize=(5,4))
    plt.plot(recall, precision, label=f"PR-AUC={pr_auc:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    prc_path = "reports/metrics/precision_recall_curve.png"
    save_plot(prc_path)

    # ======== Feature Importance ==========
    importances = model.feature_importances_
    sorted_idx = importances.argsort()

    plt.figure(figsize=(7,5))
    plt.barh(range(len(importances)), importances[sorted_idx])
    plt.yticks(range(len(importances)), [feature_names[i] for i in sorted_idx])
    plt.title("Feature Importance")
    fi_path = "reports/metrics/feature_importance.png"
    save_plot(fi_path)

    # ======== Calibration Curve ==========
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)

    plt.figure(figsize=(5,4))
    plt.plot(prob_pred, prob_true, marker="o", label="Model Calibration")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("Predicted Probability")
    plt.ylabel("True Probability")
    plt.title("Calibration Curve")
    cal_path = "reports/metrics/calibration_curve.png"
    save_plot(cal_path)

    # ======== MLflow Logging ==========
    mlflow.log_metric("test_accuracy", accuracy)
    mlflow.log_metric("AUC", auc)
    mlflow.log_metric("PR_AUC", pr_auc)
    mlflow.log_artifact(report_path)
    mlflow.log_artifact(roc_path)
    mlflow.log_artifact(prc_path)
    mlflow.log_artifact(fi_path)
    mlflow.log_artifact(cal_path)

    print("✔ Advanced evaluation plots saved & logged to MLflow")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    main(args.model, args.test, args.out)
