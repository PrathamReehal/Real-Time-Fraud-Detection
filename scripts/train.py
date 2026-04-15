"""
Train fraud detection model.

Usage: python scripts/train.py
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

DATASET_PATH = "ml/dataset.csv"
MODEL_OUTPUT = "ml/fraud_model.pkl"

NUMERIC = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
CATEGORICAL = ['type']


def train():
    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    df = df.drop(["step", "nameOrig", "nameDest", "isFlaggedFraud"], axis=1)
    
    X = df.drop('isFraud', axis=1)
    y = df['isFraud']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )
    
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUMERIC),
        ("cat", OneHotEncoder(drop="first"), CATEGORICAL),
    ], remainder="drop")
    
    pipeline = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000))
    ])
    
    print("Training...")
    pipeline.fit(X_train, y_train)
    
    print(f"Accuracy: {pipeline.score(X_test, y_test):.4f}")
    
    joblib.dump(pipeline, MODEL_OUTPUT)
    print(f"Saved to {MODEL_OUTPUT}")


if __name__ == "__main__":
    train()
