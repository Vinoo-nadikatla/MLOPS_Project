# src/data/preprocess.py

import argparse
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

def main(input, output, config_output=None):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    # Load data
    df = pd.read_csv(input)
    logging.info(f"Raw data shape: {df.shape}")
    
    # Handle missing values properly
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            df[col] = df[col].fillna(df[col].median())

    logging.info(f"NA values after cleaning: {df.isnull().sum().sum()}")

    # Identify target column (last column)
    target_col = df.columns[-1]
    X = df.drop(columns=[target_col]).copy()
    y = df[target_col].copy()
    
    # Identify data types
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()

    logging.info(f"Categorical columns: {categorical_cols}")
    logging.info(f"Numeric columns: {numeric_cols}")
    logging.info(f"Target column: {target_col}")

    # Label encoders for non-numeric features → convert to numeric
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le.classes_.tolist()
        logging.info(f"Encoded {col} with {len(le.classes_)} classes")

    # Ensure target is numeric too
    if y.dtype == 'object':
        target_le = LabelEncoder()
        y = target_le.fit_transform(y)
        label_encoders[target_col] = target_le.classes_.tolist()

    # Create final processed dataset
    processed_df = X.copy()
    processed_df[target_col] = y

    # Save final output
    processed_df.to_csv(output, index=False)
    logging.info(f"Preprocessed data saved to {output} (shape: {processed_df.shape})")

    # Save preprocessing metadata
    if config_output:
        config = {
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'target_col': target_col,
            'label_encoders': label_encoders
        }
        os.makedirs(os.path.dirname(config_output), exist_ok=True)
        with open(config_output, 'w') as f:
            json.dump(config, f, indent=2)
        logging.info(f"Preprocessing config saved to {config_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config-output", default=None)
    args = parser.parse_args()
    main(args.input, args.output, args.config_output)
