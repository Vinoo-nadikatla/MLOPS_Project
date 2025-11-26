import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import mlflow

def train():
    df = pd.read_csv('data/processed/processed.csv')
    X = df.drop('target', axis=1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    mlflow.set_experiment("heart")
    with mlflow.start_run():
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        mlflow.sklearn.log_model(model, "model")
        joblib.dump(model, "models/model.pkl")

if __name__ == "__main__":
    train()
