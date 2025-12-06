import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import mlflow
import yaml
from two_stage_model import TwoStageModel


def main(train, model, params, test_out=None):
    # Ensure model directory exists
    os.makedirs(os.path.dirname(model), exist_ok=True)

    # Ensure test_out directory exists only if provided
    if test_out is not None and test_out != "":
        os.makedirs(os.path.dirname(test_out), exist_ok=True)

    # Load training parameters
    with open(params) as f:
        p = yaml.safe_load(f)

    df = pd.read_csv(train)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # First split off a test set (15% of data)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X,
        y,
        test_size=0.15,
        random_state=p["train"]["random_state"],
        stratify=y,
    )

    # Split remaining into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=p["train"]["test_size"],
        random_state=p["train"]["random_state"],
        stratify=y_temp,
    )

    # Optionally save an independent test set
    if test_out is not None and test_out != "":
        test_df = X_test.copy()
        test_df["target"] = y_test
        test_df.to_csv(test_out, index=False)

    mlflow.set_experiment("health_experiment")

    with mlflow.start_run():
        # Train the two-stage model
        two_stage_model = TwoStageModel()
        two_stage_model.fit(X_train, y_train)

        # Validation accuracy
        val_pred = two_stage_model.predict_labels(X_val)
        val_acc = (val_pred == y_val.values).mean()

        mlflow.log_metric("validation_accuracy", float(val_acc))

        # Save trained model
        two_stage_model.save(model)
        mlflow.log_artifact(model)

    print("✓ Training Complete!")
    print(f"Validation Accuracy: {val_acc:.4f}")
    print(f"Model saved to: {model}")
    if test_out is not None and test_out != "":
        print(f"Test set saved to: {test_out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True, help="Path to processed training CSV")
    parser.add_argument("--model", required=True, help="Path to save trained model (pickle)")
    parser.add_argument("--params", required=True, help="YAML file with training hyperparameters")
    parser.add_argument(
        "--test-out",
        default=None,
        help="Optional path to save an independent test set CSV.",
    )
    args = parser.parse_args()

    main(args.train, args.model, args.params, args.test_out)
