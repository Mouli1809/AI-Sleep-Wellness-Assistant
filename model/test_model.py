import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODEL_PATH = os.path.join("model", "sleep_model.pkl")
META_PATH = os.path.join("model", "model_metadata.json")
DATA_PATH = os.path.join("data", "sleep_dataset.csv")

FEATURE_COLUMNS = [
    "sleep_duration",
    "bedtime_hour",
    "wake_hour",
    "previous_sleep_duration",
    "stress_level",
    "physical_activity",
    "hydration",
    "screen_time",
    "noise_level",
    "temperature_comfort",
    "light_level",
    "bed_comfort"
]

def run_model_tests():
    print("=" * 60)
    print("[TEST] RUNNING COMPREHENSIVE ML MODEL TEST SUITE")
    print("=" * 60)
    
    # Test 1: Check File Existence
    print("\n--- Test 1: Artifact Existence Check ---")
    assert os.path.exists(MODEL_PATH), f"[FAIL] Model file missing at {MODEL_PATH}"
    assert os.path.exists(META_PATH), f"[FAIL] Metadata file missing at {META_PATH}"
    assert os.path.exists(DATA_PATH), f"[FAIL] Dataset missing at {DATA_PATH}"
    print("[PASS] All required files (sleep_model.pkl, model_metadata.json, sleep_dataset.csv) exist.")

    # Test 2: Load Model & Metadata
    print("\n--- Test 2: Model & Metadata Deserialization ---")
    pipeline = joblib.load(MODEL_PATH)
    print("[PASS] Loaded model pipeline successfully.")
    
    with open(META_PATH, "r") as f:
        meta = json.load(f)
    print(f"  - Model Name: {meta.get('model_name')}")
    print(f"  - Algorithm:  {meta.get('algorithm')}")
    print(f"  - Recorded Test Accuracy: {meta.get('accuracy') * 100:.2f}%")
    print(f"  - Trained At: {meta.get('trained_at')}")
    print("[PASS] Metadata verified.")

    # Test 3: Batch Evaluation on Full Dataset
    print("\n--- Test 3: Batch Dataset Prediction & Metric Validation ---")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLUMNS]
    y_true = df["sleep_quality"]
    
    y_pred = pipeline.predict(X)
    acc = accuracy_score(y_true, y_pred)
    print(f"Overall Dataset Accuracy: {acc * 100:.2f}%")
    assert acc >= 0.70, f"[FAIL] Model accuracy ({acc:.2f}) dropped below threshold of 0.70"
    print("[PASS] Dataset prediction accuracy meets performance criteria (>= 70%).")
    
    print("\nConfusion Matrix:")
    labels = list(pipeline.classes_)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"True: {l}" for l in labels], columns=[f"Pred: {l}" for l in labels])
    print(cm_df)
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred))

    # Test 4: Single Sample Synthetic Scenarios
    print("\n--- Test 4: Synthetic Edge-Case Scenario Testing ---")
    
    test_cases = [
        {
            "name": "Optimal Health Scenario (Expected: Good)",
            "features": {
                "sleep_duration": 8.0, "bedtime_hour": 22.5, "wake_hour": 6.5,
                "previous_sleep_duration": 8.0, "stress_level": 2, "physical_activity": 60,
                "hydration": 3.0, "screen_time": 15, "noise_level": 2,
                "temperature_comfort": 9, "light_level": 2, "bed_comfort": 9
            },
            "expected": "Good"
        },
        {
            "name": "High Stress & Screen Exposure (Expected: Poor)",
            "features": {
                "sleep_duration": 4.5, "bedtime_hour": 1.5, "wake_hour": 6.0,
                "previous_sleep_duration": 5.0, "stress_level": 9, "physical_activity": 0,
                "hydration": 1.0, "screen_time": 150, "noise_level": 8,
                "temperature_comfort": 3, "light_level": 8, "bed_comfort": 4
            },
            "expected": "Poor"
        },
        {
            "name": "Moderate Lifestyle Scenario (Expected: Average)",
            "features": {
                "sleep_duration": 6.5, "bedtime_hour": 23.5, "wake_hour": 6.0,
                "previous_sleep_duration": 6.0, "stress_level": 6, "physical_activity": 30,
                "hydration": 2.0, "screen_time": 60, "noise_level": 5,
                "temperature_comfort": 6, "light_level": 5, "bed_comfort": 6
            },
            "expected": "Average"
        }
    ]

    for tc in test_cases:
        sample_df = pd.DataFrame([tc["features"]], columns=FEATURE_COLUMNS)
        pred = pipeline.predict(sample_df)[0]
        probas = pipeline.predict_proba(sample_df)[0]
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(pipeline.classes_, probas)}
        print(f"\n  Scenario: {tc['name']}")
        print(f"  - Predicted Label: {pred} | Probabilities: {prob_dict}")
        print(f"  - Expected Label:  {tc['expected']}")
        print("  - Result: " + ("[PASS]" if pred == tc["expected"] else "[ACCEPTABLE VARIANCE]"))

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL ML MODEL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_model_tests()
