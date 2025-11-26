import pandas as pd
import joblib
from sklearn.metrics import accuracy_score

def evaluate():
    df = pd.read_csv('data/processed/processed.csv')
    X = df.drop('target', axis=1)
    y = df['target']

    model = joblib.load("models/model.pkl")
    preds = model.predict(X)
    print("Accuracy:", accuracy_score(y, preds))

if __name__ == "__main__":
    evaluate()
