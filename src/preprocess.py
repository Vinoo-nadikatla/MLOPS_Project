import pandas as pd

def preprocess():
    df = pd.read_csv('data/raw/heart.csv')
    df = df.dropna()
    df.to_csv('data/processed/processed.csv', index=False)

if __name__ == "__main__":
    preprocess()
