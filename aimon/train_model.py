#!/usr/bin/env python3
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

DATA_PATH = "/opt/aimon/data/baseline_training.csv"
MODEL_PATH = "/opt/aimon/models/isolation_forest.joblib"

df = pd.read_csv(DATA_PATH)
features = ["cpu_percent", "mem_percent", "data_usage_percent", "logs_usage_percent"]

model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(df[features])

joblib.dump(model, MODEL_PATH)
print(f"Model successfully trained and saved to {MODEL_PATH}")
