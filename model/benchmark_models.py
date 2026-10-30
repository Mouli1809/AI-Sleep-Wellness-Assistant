
import os
import json
import warnings
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    RandomForestClassifier,
    HistGradientBoostingClassifier
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix
)

warnings.filterwarnings("ignore")

# ==========================================
# 1. PROJECT PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(
    PROJECT_DIR, "data", "sleep_dataset.csv"
)

MODEL_DIR = BASE_DIR

BENCHMARK_PATH = os.path.join(
    MODEL_DIR, "model_benchmarks.json"
)

REPORT_PATH = os.path.join(
    MODEL_DIR, "classification_reports.json"
)

CONFUSION_PATH = os.path.join(
    MODEL_DIR, "confusion_matrices.json"
)

# ==========================================
# 2. FEATURE COLUMNS
# ==========================================

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

TARGET_COLUMN = "sleep_quality"

# ==========================================
# 3. LOAD AND VALIDATE DATASET
# ==========================================

def load_dataset():

    print("\nLoading Sleep Dataset...")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    df = df[required_columns].copy()

    # Convert input features to numeric
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    # Remove records without target labels
    df = df.dropna(subset=[TARGET_COLUMN])

    # Remove infinite values
    df[FEATURE_COLUMNS] = df[
        FEATURE_COLUMNS
    ].replace([np.inf, -np.inf], np.nan)

    if df[TARGET_COLUMN].nunique() < 2:
        raise ValueError(
            "At least two target classes are required."
        )

    print("Dataset loaded successfully!")
    print("Total records:", len(df))
    print("Features:", len(FEATURE_COLUMNS))
    print("\nClass Distribution:")
    print(df[TARGET_COLUMN].value_counts())

    return df


# ==========================================
# 4. DEFINE ML MODELS
# ==========================================

def get_models():

    models = {

        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=120,
                max_depth=12,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1
            ))
        ]),

        "HistGradientBoosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", HistGradientBoostingClassifier(
                random_state=42
            ))
        ]),

        "Decision Tree": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", DecisionTreeClassifier(
                max_depth=8,
                random_state=42,
                class_weight="balanced"
            ))
        ]),

        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight="balanced"
            ))
        ])
    }

    return models


# ==========================================
# 5. MODEL BENCHMARKING
# ==========================================

def run_benchmarks():

    os.makedirs(MODEL_DIR, exist_ok=True)

    df = load_dataset()

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].astype(str)

    # Check whether stratified splitting is possible
    if y.value_counts().min() < 2:
        raise ValueError(
            "Each class must contain at least 2 records "
            "for stratified train-test splitting."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("\nTraining records:", len(X_train))
    print("Testing records:", len(X_test))

    models = get_models()

    results = {}
    reports = {}
    matrices = {}

    best_model_name = None
    best_model = None
    best_accuracy = -1

    # ======================================
    # TRAIN AND EVALUATE EACH MODEL
    # ======================================

    for name, model in models.items():

        print("\n" + "=" * 55)
        print("Training:", name)
        print("=" * 55)

        try:

            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)

            f1 = f1_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )

            precision = precision_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )

            recall = recall_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )

            # Store evaluation metrics
            results[name] = {
                "Accuracy": round(acc * 100, 2),
                "F1-Score": round(f1 * 100, 2),
                "Precision": round(precision * 100, 2),
                "Recall": round(recall * 100, 2)
            }

            # Classification report
            reports[name] = classification_report(
                y_test,
                y_pred,
                output_dict=True,
                zero_division=0
            )

            # Confusion matrix
            labels = sorted(y.unique())

            cm = confusion_matrix(
                y_test,
                y_pred,
                labels=labels
            )

            matrices[name] = {
                "labels": labels,
                "matrix": cm.tolist()
            }

            print(f"Accuracy  : {acc * 100:.2f}%")
            print(f"F1-Score  : {f1 * 100:.2f}%")
            print(f"Precision : {precision * 100:.2f}%")
            print(f"Recall    : {recall * 100:.2f}%")

            print("\nClassification Report:")
            print(classification_report(
                y_test,
                y_pred,
                zero_division=0
            ))

            # Select best model using accuracy
            if acc > best_accuracy:
                best_accuracy = acc
                best_model_name = name
                best_model = model

        except Exception as e:

            print(f"ERROR training {name}: {e}")

    if not results:
        raise RuntimeError(
            "All model training attempts failed."
        )

    # ======================================
    # 6. SAVE RESULTS
    # ======================================

    with open(BENCHMARK_PATH, "w") as f:
        json.dump(results, f, indent=4)

    with open(REPORT_PATH, "w") as f:
        json.dump(reports, f, indent=4)

    with open(CONFUSION_PATH, "w") as f:
        json.dump(matrices, f, indent=4)

    # ======================================
    # 7. FINAL RESULTS
    # ======================================

    print("\n" + "=" * 60)
    print("FINAL MODEL BENCHMARK RESULTS")
    print("=" * 60)

    results_df = pd.DataFrame(results).T
    print(results_df.to_string())

    print("\n" + "=" * 60)
    print("BEST PERFORMING MODEL")
    print("=" * 60)

    print("Model Name:", best_model_name)
    print(
        "Accuracy:",
        f"{best_accuracy * 100:.2f}%"
    )

    print("\nSaved Files:")
    print(BENCHMARK_PATH)
    print(REPORT_PATH)
    print(CONFUSION_PATH)

    return results, best_model_name, best_model


# ==========================================
# 8. MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    try:

        results, best_name, best_model = run_benchmarks()

        print("\nBenchmarking completed successfully!")

    except Exception as e:

        print("\nPROJECT ERROR:", str(e))
        raise
