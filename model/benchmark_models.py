import os
import json
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

DATA_PATH = os.path.join("data", "sleep_dataset.csv")
BENCHMARK_PATH = os.path.join("model", "model_benchmarks.json")

FEATURE_COLUMNS = [
    "sleep_duration", "bedtime_hour", "wake_hour", "previous_sleep_duration",
    "stress_level", "physical_activity", "hydration", "screen_time",
    "noise_level", "temperature_comfort", "light_level", "bed_comfort"
]

def run_benchmarks():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset missing at {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y = df["sleep_quality"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    models = {
        "Random Forest": Pipeline([("scaler", StandardScaler()), ("rf", RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42))]),
        "HistGradientBoosting": Pipeline([("scaler", StandardScaler()), ("hgb", HistGradientBoostingClassifier(random_state=42))]),
        "Decision Tree": Pipeline([("scaler", StandardScaler()), ("dt", DecisionTreeClassifier(max_depth=8, random_state=42))]),
        "Logistic Regression": Pipeline([("scaler", StandardScaler()), ("lr", LogisticRegression(max_iter=1000, random_state=42))])
    }
    
    results = {}
    
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, average="weighted"))
        prec = float(precision_score(y_test, y_pred, average="weighted"))
        rec = float(recall_score(y_test, y_pred, average="weighted"))
        
        results[name] = {
            "Accuracy": round(acc * 100, 2),
            "F1-Score": round(f1 * 100, 2),
            "Precision": round(prec * 100, 2),
            "Recall": round(rec * 100, 2)
        }
        print(f"[BENCHMARK] {name:22s} -> Accuracy: {acc*100:.2f}% | F1: {f1*100:.2f}%")
        
    os.makedirs(os.path.dirname(BENCHMARK_PATH), exist_ok=True)
    with open(BENCHMARK_PATH, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\nSaved algorithm benchmark results to {BENCHMARK_PATH}")
    return results

if __name__ == "__main__":
    run_benchmarks()
