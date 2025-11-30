# src/models/evaluate.py
import argparse
import joblib
import pandas as pd
import os

def main(model, test, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    clf = joblib.load(model)
    df = pd.read_csv(test)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    acc = clf.score(X, y)
    with open(out, "w") as f:
        f.write(f"accuracy: {acc:.4f}\n")
    print(f"Evaluation written to {out}. Acc: {acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    main(args.model, args.test, args.out)
