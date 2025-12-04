# src/reports/eda.py

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def save_plot(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path, bbox_inches="tight")
    plt.close()

def run_eda(input_path):
    print(f"Loading dataset from: {input_path}")

    df = pd.read_csv(input_path)
    print(f"Dataset Shape: {df.shape}")
    print("\nColumn Details:")
    print(df.dtypes)

    # Summary stats
    stats_path = "reports/figures/data_summary.txt"
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)
    with open(stats_path, "w") as f:
        f.write("===== DATASET SUMMARY =====\n")
        f.write(str(df.describe(include="all")))
        f.write("\n\nMissing Values:\n")
        f.write(str(df.isnull().sum()))

    print(f"Data summary saved to {stats_path}")

    # Target distribution
    target = df.columns[-1]
    plt.figure(figsize=(5,4))
    sns.countplot(data=df, x=target, palette="Set2")
    plt.title("Target Class Distribution")
    save_plot("reports/figures/class_distribution.png")

    # Numeric distributions
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    for col in num_cols:
        plt.figure()
        sns.histplot(df[col], kde=True)
        plt.title(f"Distribution: {col}")
        save_plot(f"reports/figures/distribution_{col}.png")

    # Boxplots for outliers
    for col in num_cols:
        plt.figure()
        sns.boxplot(x=df[col], color="orange")
        plt.title(f"Outliers in {col}")
        save_plot(f"reports/figures/outliers_{col}.png")

    # Correlation heatmap
    plt.figure(figsize=(10,8))
    sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    save_plot("reports/figures/correlation_heatmap.png")

    # Pairplot for key features (top correlated)
    top_corr = (
        df[num_cols].corr()[target]
        .abs()
        .sort_values(ascending=False)[:5]
        .index.tolist()
    )
    sns.pairplot(df[top_corr], diag_kind="kde")
    save_plot("reports/figures/top_features_pairplot.png")

    # Feature importance (only if preprocessed + trained model exists)
    model_path = "models/model.pkl"
    if os.path.exists(model_path):
        import joblib
        model_dict = joblib.load(model_path)
        model = model_dict["rf_model"]
        feature_names = model_dict["feature_names"]

        importances = model.feature_importances_
        sorted_idx = importances.argsort()

        plt.figure(figsize=(8,6))
        plt.barh(range(len(importances)), importances[sorted_idx])
        plt.yticks(range(len(importances)), [feature_names[i] for i in sorted_idx])
        plt.title("Feature Importance (from model)")
        save_plot("reports/figures/feature_importance.png")

    print("📊 EDA Completed Successfully! All plots saved to reports/figures/")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Heart Disease Dataset EDA")
    parser.add_argument("--input", required=True, help="Path to dataset CSV")
    args = parser.parse_args()
    run_eda(args.input)
