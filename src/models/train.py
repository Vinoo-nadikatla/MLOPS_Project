import argparse
import os

import mlflow
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ParameterGrid, train_test_split

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

    train_cfg = p.get("train", {})
    hp_cfg = p.get("hyperparam_search", {})
    hp_enabled = hp_cfg.get("enabled", False)

    df = pd.read_csv(train)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # First split off a test set (15% of data)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X,
        y,
        test_size=0.15,
        random_state=train_cfg.get("random_state", 42),
        stratify=y,
    )

    # Split remaining into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=train_cfg.get("test_size", 0.2),
        random_state=train_cfg.get("random_state", 42),
        stratify=y_temp,
    )

    # Optionally save an independent test set
    if test_out is not None and test_out != "":
        test_df = X_test.copy()
        test_df["target"] = y_test
        test_df.to_csv(test_out, index=False)

    mlflow.set_experiment("health_experiment")

    with mlflow.start_run():
        # =====================================================
        # Hyperparameter tuning (optional grid search)
        # =====================================================
        if hp_enabled:
            grid_cfg = hp_cfg.get("grid", {})
            param_grid = {}

            # Convert YAML null -> Python None where needed
            for k, v_list in grid_cfg.items():
                param_grid[k] = [(None if vv is None else vv) for vv in v_list]

            best_acc = -1.0
            best_params = None

            if len(param_grid) > 0:
                for params_dict in ParameterGrid(param_grid):
                    # Include original baseline as one candidate in the grid
                    rf = RandomForestClassifier(
                        random_state=train_cfg.get("random_state", 42),
                        **params_dict,
                    )
                    candidate_model = TwoStageModel(rf_model=rf)
                    candidate_model.fit(X_train, y_train)

                    val_pred = candidate_model.predict_labels(X_val)
                    val_acc = (val_pred == y_val.values).mean()

                    if val_acc > best_acc:
                        best_acc = val_acc
                        best_params = params_dict

                # Log best params and best validation accuracy
                if best_params is not None:
                    mlflow.log_params(
                        {f"rf__{k}": v for k, v in best_params.items()}
                    )
                    mlflow.log_metric("best_val_accuracy", float(best_acc))

                # Retrain final model on train+val with best params
                X_full = pd.concat([X_train, X_val], axis=0)
                y_full = pd.concat([y_train, y_val], axis=0)

                if best_params is not None:
                    final_rf = RandomForestClassifier(
                        random_state=train_cfg.get("random_state", 42),
                        **best_params,
                    )
                else:
                    # Fallback to baseline if something went wrong
                    final_rf = RandomForestClassifier(
                        n_estimators=train_cfg.get("n_estimators", 100),
                        random_state=train_cfg.get("random_state", 42),
                    )

                two_stage_model = TwoStageModel(rf_model=final_rf)
                two_stage_model.fit(X_full, y_full)
                val_acc = best_acc if best_acc > 0 else val_acc

            else:
                # Grid is empty: behave like original code
                two_stage_model = TwoStageModel()
                two_stage_model.fit(X_train, y_train)
                val_pred = two_stage_model.predict_labels(X_val)
                val_acc = (val_pred == y_val.values).mean()

        else:
            # =====================================================
            # Original behaviour (no tuning)
            # =====================================================
            two_stage_model = TwoStageModel()
            two_stage_model.fit(X_train, y_train)

            # Validation accuracy
            val_pred = two_stage_model.predict_labels(X_val)
            val_acc = (val_pred == y_val.values).mean()

        # Log final validation accuracy
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
