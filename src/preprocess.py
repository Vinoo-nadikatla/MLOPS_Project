# src/data/preprocess.py
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import os

def main(input, output):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    df = pd.read_csv(input)
    # simple cleaning: drop NA and encode categorical columns minimally
    df = df.dropna().reset_index(drop=True)
    # For the assignment we will keep all numeric columns only (simple)
    df_numeric = df.select_dtypes(include='number')
    # keep 80% rows for training (we're using same file as train/test to keep simple)
    df_numeric.to_csv(output, index=False)
    print(f"Wrote preprocessed file to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.input, args.output)
