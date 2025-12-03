# src/data/preprocess.py
import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os
import json

def main(input, output, config_output=None):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Load data
    df = pd.read_csv(input)
    print(f"Raw data shape: {df.shape}")
    
    # Step 1: Handle missing values
    print(f"Missing values before cleaning: {df.isnull().sum().sum()}")
    df = df.dropna().reset_index(drop=True)
    print(f"Data shape after dropping NA: {df.shape}")
    
    # Step 2: Identify target column (last column, typically 'target' or disease indicator)
    target_col = df.columns[-1]
    feature_cols = df.columns[:-1]
    
    # Step 3: Separate features and target
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # Step 4: Identify categorical and numeric columns
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()
    
    print(f"Categorical columns: {categorical_cols}")
    print(f"Numeric columns: {numeric_cols}")
    
    # Step 5: Encode categorical columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le.classes_.tolist()
    
    # Step 6: Scale numeric features
    scaler = StandardScaler()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    
    # Step 7: Ensure target is numeric (encode if categorical)
    if y.dtype == 'object':
        y_le = LabelEncoder()
        y = y_le.fit_transform(y)
        label_encoders['target'] = y_le.classes_.tolist()
    
    # Step 8: Combine processed features and target
    X['target'] = y
    
    # Step 9: Save preprocessed data
    X.to_csv(output, index=False)
    print(f"Preprocessed data saved to {output}")
    print(f"Preprocessed data shape: {X.shape}")
    
    # Step 10: Save preprocessing config for later use (inference)
    if config_output:
        config = {
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'label_encoders': label_encoders,
            'scaler_mean': scaler.mean_.tolist(),
            'scaler_scale': scaler.scale_.tolist()
        }
        os.makedirs(os.path.dirname(config_output), exist_ok=True)
        with open(config_output, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Preprocessing config saved to {config_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw CSV file")
    parser.add_argument("--output", required=True, help="Path to save preprocessed CSV")
    parser.add_argument("--config-output", default=None, help="Path to save preprocessing config JSON")
    args = parser.parse_args()
    main(args.input, args.output, args.config_output)
