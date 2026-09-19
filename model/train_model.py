import os
import json
import joblib
import datetime
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score

FEATURE_COLUMNS = [
    "sleep_duration", "bedtime_hour", "wake_hour", "previous_sleep_duration",
    "stress_level", "physical_activity", "hydration", "screen_time",
    "noise_level", "temperature_comfort", "light_level", "bed_comfort"
]
TARGET_COLUMN = "sleep_quality"


def build_models():
    return {
        "HistGradientBoosting": Pipeline([
            ("scaler", StandardScaler()),
            ("model", HistGradientBoostingClassifier(random_state=42))
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1))
        ]),
        "Decision Tree": Pipeline([
            ("scaler", StandardScaler()),
            ("model", DecisionTreeClassifier(max_depth=8, random_state=42))
        ]),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, random_state=42))
        ])
    }


def train_and_save_model(data_path="data/sleep_dataset.csv", model_dir="model"):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")

    df = pd.read_csv(data_path)
    X, y = df[FEATURE_COLUMNS], df[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = {}
    fitted = {}
    for name, pipeline in build_models().items():
        pipeline.fit(X_train, y_train)
        pred = pipeline.predict(X_test)
        results[name] = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "f1_score": round(float(f1_score(y_test, pred, average="weighted")), 4),
            "precision": round(float(precision_score(y_test, pred, average="weighted")), 4),
            "recall": round(float(recall_score(y_test, pred, average="weighted")), 4),
        }
        fitted[name] = pipeline
        print(f"{name:22s}: accuracy={results[name]['accuracy']*100:.2f}% | F1={results[name]['f1_score']*100:.2f}%")

    # Select the model using unseen-test weighted F1, then accuracy as tie-breaker.
    selected_name = max(results, key=lambda n: (results[n]["f1_score"], results[n]["accuracy"]))
    pipeline = fitted[selected_name]
    y_pred = pipeline.predict(X_test)
    test_acc = float(accuracy_score(y_test, y_pred))

    # Model-agnostic feature importance using permutation importance on the held-out test set.
    perm = permutation_importance(
        pipeline, X_test, y_test, n_repeats=8, random_state=42, scoring="f1_weighted", n_jobs=-1
    )
    importances = dict(zip(FEATURE_COLUMNS, [float(v) for v in perm.importances_mean]))
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "sleep_model.pkl")
    meta_path = os.path.join(model_dir, "model_metadata.json")
    benchmarks_path = os.path.join(model_dir, "model_benchmarks.json")

    joblib.dump(pipeline, model_path)

    metadata = {
        "model_name": f"{selected_name} Sleep Quality Classifier",
        "algorithm": selected_name,
        "accuracy": round(test_acc, 4),
        "train_accuracy": round(float(accuracy_score(y_train, pipeline.predict(X_train))), 4),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "classes": [str(c) for c in pipeline.classes_],
        "feature_importances": sorted_importances,
        "model_selection_metric": "weighted F1 on stratified 20% hold-out test set",
        "trained_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sklearn_version": __import__("sklearn").__version__,
        "dataset_type": "synthetic demonstration dataset"
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    with open(benchmarks_path, "w") as f:
        json.dump({k: {kk: round(vv * 100, 2) for kk, vv in v.items()} for k, v in results.items()}, f, indent=2)

    print(f"\nSelected model: {selected_name}")
    print(f"Held-out test accuracy: {test_acc*100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print(f"Saved model to {model_path}")
    return model_path, meta_path


if __name__ == "__main__":
    train_and_save_model()
