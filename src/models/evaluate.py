# src/models/evaluate.py

import argparse
import json
import os

import joblib
import mlflow
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def save_plot(path: str) -> None:
    """Save current matplotlib figure to disk and close it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def main(model_path: str, test_path: str, report_path: str) -> None:
    # Ensure report directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # -----------------------------
    # 1. Load model and test data
    # -----------------------------
    model_dict = joblib.load(model_path)

    # Prefer calibrated model if available, otherwise use RF
    model = model_dict.get("calibrated_model", model_dict["rf_model"])

    # Feature names with a safe fallback
    feature_names = model_dict.get("feature_names", None)

    df = pd.read_csv(test_path)
    X_test = df.iloc[:, :-1]
    y_test = df.iloc[:, -1]

    if feature_names is None:
        feature_names = list(X_test.columns)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # -----------------------------
    # 2. Metrics (scalar)
    # -----------------------------
    accuracy = accuracy_score(y_test, y_pred)
    brier = brier_score_loss(y_test, y_prob)

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # ROC / PR metrics
    auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)

    # Confusion matrix & derived counts
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    n_samples = int(len(y_test))
    n_positive = int(y_test.sum())
    n_negative = int(n_samples - n_positive)

    # Text and JSON classification reports
    report_text = classification_report(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, output_dict=True)

    # -----------------------------
    # 3. Write reports to disk
    # -----------------------------
    # Human-readable text report
    with open(report_path, "w") as f:
        f.write(f"Test samples: {n_samples}\n")
        f.write(f"Positives: {n_positive}, Negatives: {n_negative}\n\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(f"Brier score: {brier:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1-score: {f1:.4f}\n")
        f.write(f"ROC AUC: {auc:.4f}\n")
        f.write(f"PR AUC: {pr_auc:.4f}\n")
        f.write(f"Specificity: {specificity:.4f}\n\n")
        f.write(report_text)

    # Machine-readable JSON report
    report_json_path = os.path.join(
        os.path.dirname(report_path), "classification_report.json"
    )
    with open(report_json_path, "w") as jf:
        json.dump(report_dict, jf, indent=2)

    print(f"✓ Test Accuracy: {accuracy:.4f}")

    # -----------------------------
    # 4. Plots
    # -----------------------------
    # ROC curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, label=f"AUC={auc:.3f}")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    roc_path = "reports/metrics/roc_curve.png"
    save_plot(roc_path)

    # Precision–Recall curve
    precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_prob)
    plt.figure(figsize=(5, 4))
    plt.plot(recall_curve, precision_curve, label=f"PR-AUC={pr_auc:.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision–Recall Curve")
    plt.legend()
    prc_path = "reports/metrics/precision_recall_curve.png"
    save_plot(prc_path)

    # Confusion matrix heatmap
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    cm_path = "reports/metrics/confusion_matrix.png"
    save_plot(cm_path)

    # Feature importance
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        sorted_idx = importances.argsort()

        plt.figure(figsize=(7, 5))
        plt.barh(range(len(importances)), importances[sorted_idx])
        plt.yticks(
            range(len(importances)),
            [feature_names[i] for i in sorted_idx],
        )
        plt.title("Feature Importance")
        fi_path = "reports/metrics/feature_importance.png"
        save_plot(fi_path)
    else:
        fi_path = None

    # Calibration curve
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
    plt.figure(figsize=(5, 4))
    plt.plot(prob_pred, prob_true, marker="o", label="Model Calibration")
    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("Predicted Probability")
    plt.ylabel("True Probability")
    plt.title("Calibration Curve")
    cal_path = "reports/metrics/calibration_curve.png"
    save_plot(cal_path)

    # -----------------------------
    # 5. MLflow logging
    # -----------------------------
    mlflow.log_metric("test_accuracy", accuracy)
    mlflow.log_metric("brier_score", brier)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("AUC", auc)
    mlflow.log_metric("PR_AUC", pr_auc)
    mlflow.log_metric("specificity", specificity)
    mlflow.log_metric("n_test_samples", n_samples)
    mlflow.log_metric("n_positive", n_positive)
    mlflow.log_metric("n_negative", n_negative)

    mlflow.log_artifact(report_path)
    mlflow.log_artifact(report_json_path)
    mlflow.log_artifact(roc_path)
    mlflow.log_artifact(prc_path)
    mlflow.log_artifact(cm_path)
    if fi_path is not None:
        mlflow.log_artifact(fi_path)
    mlflow.log_artifact(cal_path)

    print("✔ Advanced evaluation metrics, plots, and reports saved & logged to MLflow")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    main(args.model, args.test, args.out)
