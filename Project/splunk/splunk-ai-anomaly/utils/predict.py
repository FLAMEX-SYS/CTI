# utils/predict.py
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_PATH = "model/anomaly_model.pkl"

def preprocess(df):
    df['hour'] = df['timestamp'].dt.hour
    df['ip_last'] = df['src_ip'].apply(lambda x: int(x.split('.')[-1]))
    return df[['hour', 'ip_last']]

def train_model(df):
    os.makedirs("model", exist_ok=True)
    X = preprocess(df)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    return model

def predict_anomalies(df, model=None):
    if model is None:
        model = joblib.load(MODEL_PATH)
    X = preprocess(df)
    preds = model.predict(X)
    df['anomaly'] = preds
    df['anomaly'] = df['anomaly'].map({1: "Normal", -1: "Anomaly"})
    return df
