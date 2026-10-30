
import os
import json
import joblib
import datetime
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
    cross_val_score
)
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    HistGradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score
)

FEATURE_COLUMNS = [
    "sleep_duration", "bedtime_hour", "wake_hour",
    "previous_sleep_duration", "stress_level",
    "physical_activity", "hydration", "screen_time",
    "noise_level", "temperature_comfort",
    "light_level", "bed_comfort"
]

TARGET_COLUMN = "sleep_quality"
RANDOM_STATE = 42


def build_spline_logreg():
    other_cols = [
        c for c in FEATURE_COLUMNS
        if c != "sleep_duration"
    ]

    features = ColumnTransformer([
        (
            "duration_curve",
            SplineTransformer(
                n_knots=6,
                degree=3,
                extrapolation="linear"
            ),
            ["sleep_duration"]
        ),
        ("other", "passthrough", other_cols)
    ])

    return Pipeline([
        ("features", features),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=5000,
            random_state=RANDOM_STATE
        ))
    ])


def build_search_models():

    return {
        "Extra Trees": (
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("classifier", ExtraTreesClassifier(
                    random_state=RANDOM_STATE,
                    n_jobs=1
                ))
            ]),
            {
                "classifier__n_estimators": [200, 300, 500],
                "classifier__max_depth": [None, 12, 18, 24],
                "classifier__min_samples_split": [2, 4, 8],
                "classifier__min_samples_leaf": [1, 2, 3],
                "classifier__max_features": ["sqrt", 0.8, 1.0]
            }
        ),

        "Random Forest": (
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("classifier", RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    n_jobs=1
                ))
            ]),
            {
                "classifier__n_estimators": [200, 300, 500],
                "classifier__max_depth": [None, 12, 18, 24],
                "classifier__min_samples_split": [2, 4, 8],
                "classifier__min_samples_leaf": [1, 2, 3],
                "classifier__max_features": ["sqrt", 0.8, 1.0]
            }
        ),

        "HistGradientBoosting": (
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("classifier", HistGradientBoostingClassifier(
                    random_state=RANDOM_STATE
                ))
            ]),
            {
                "classifier__max_iter": [100, 150, 200, 300],
                "classifier__learning_rate": [0.03, 0.05, 0.08, 0.1],
                "classifier__max_leaf_nodes": [15, 20, 31, 40],
                "classifier__min_samples_leaf": [10, 15, 20, 30],
                "classifier__l2_regularization": [0, 0.1, 0.5, 1.0]
            }
        )
    }


def train_and_save_model(
    data_path="data/sleep_dataset.csv",
    model_dir="model"
):

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Dataset not found: {data_path}"
        )

    df = pd.read_csv(data_path)

    required = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].copy()

    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=[TARGET_COLUMN])

    if df[FEATURE_COLUMNS].isna().any().any():
        print("Missing feature values will be imputed.")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    results = {}
    fitted_models = {}

    print("\nDataset:", len(df), "records")
    print("Training:", len(X_train))
    print("Testing:", len(X_test))

    # Existing model as a baseline
    print("\nTesting Spline Logistic Regression...")

    baseline = build_spline_logreg()

    baseline_scores = cross_val_score(
        baseline,
        X_train,
        y_train,
        cv=cv,
        scoring="accuracy",
        n_jobs=-1
    )

    baseline.fit(X_train, y_train)

    baseline_pred = baseline.predict(X_test)

    results["Spline Logistic Regression"] = {
        "cv_accuracy_mean": float(baseline_scores.mean()),
        "cv_accuracy_std": float(baseline_scores.std()),
        "test_accuracy": float(
            accuracy_score(y_test, baseline_pred)
        )
    }

    fitted_models["Spline Logistic Regression"] = baseline

    # Tune advanced models
    for name, (pipeline, parameters) in build_search_models().items():

        print("\n" + "=" * 55)
        print("Tuning:", name)
        print("=" * 55)

        search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=parameters,
            n_iter=15,
            scoring="accuracy",
            cv=cv,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            refit=True,
            verbose=1
        )

        search.fit(X_train, y_train)

        best_model = search.best_estimator_

        prediction = best_model.predict(X_test)

        test_accuracy = accuracy_score(y_test, prediction)

        results[name] = {
            "cv_accuracy_mean": float(search.best_score_),
            "cv_accuracy_std": float(
                search.cv_results_["std_test_score"][
                    search.best_index_
                ]
            ),
            "test_accuracy": float(test_accuracy),
            "best_parameters": search.best_params_
        }

        fitted_models[name] = best_model

        print("Best CV accuracy:",
              f"{search.best_score_ * 100:.2f}%")

        print("Test accuracy:",
              f"{test_accuracy * 100:.2f}%")

        print("Best parameters:", search.best_params_)

    # Select using CV only, never the test score
    selected_name = max(
        results,
        key=lambda name: results[name]["cv_accuracy_mean"]
    )

    final_model = fitted_models[selected_name]

    y_pred = final_model.predict(X_test)

    test_acc = accuracy_score(y_test, y_pred)
    train_acc = accuracy_score(
        y_train,
        final_model.predict(X_train)
    )

    weighted_f1 = f1_score(
        y_test, y_pred,
        average="weighted"
    )

    precision = precision_score(
        y_test, y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test, y_pred,
        average="weighted",
        zero_division=0
    )

    half_width = (
        1.96 * np.sqrt(
            test_acc * (1 - test_acc) / len(y_test)
        )
    )

    # Feature importance, when supported by the selected estimator
    feature_importances = {}

    if hasattr(final_model, "named_steps"):
        classifier = final_model.named_steps.get("classifier")

        if classifier is None:
            classifier = final_model.named_steps.get("model")

        if hasattr(classifier, "feature_importances_"):
            feature_importances = dict(
                zip(
                    FEATURE_COLUMNS,
                    [
                        round(float(v), 6)
                        for v in classifier.feature_importances_
                    ]
                )
            )

    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(
        model_dir, "sleep_model.pkl"
    )

    metadata_path = os.path.join(
        model_dir, "model_metadata.json"
    )

    benchmark_path = os.path.join(
        model_dir, "model_benchmarks.json"
    )

    joblib.dump(final_model, model_path)

    metadata = {
        "model_name": f"{selected_name} Sleep Quality Classifier",
        "algorithm": selected_name,
        "accuracy": round(float(test_acc), 4),
        "accuracy_ci95": [
            round(float(max(0, test_acc - half_width)), 4),
            round(float(min(1, test_acc + half_width)), 4)
        ],
        "cv_accuracy_mean": round(
            results[selected_name]["cv_accuracy_mean"], 4
        ),
        "cv_accuracy_std": round(
            results[selected_name]["cv_accuracy_std"], 4
        ),
        "train_accuracy": round(float(train_acc), 4),
        "f1_score": round(float(weighted_f1), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "classes": [str(c) for c in final_model.classes_],
        "feature_importances": feature_importances,
        "cv_benchmarks": results,
        "model_selection_metric": (
            "5-fold stratified CV accuracy on training split"
        ),
        "trained_at": datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "sklearn_version": __import__("sklearn").__version__,
        "dataset_type": "synthetic demonstration dataset"
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    benchmark_percentages = {
        name: {
            "CV Accuracy": round(
                value["cv_accuracy_mean"] * 100, 2
            ),
            "Test Accuracy": round(
                value["test_accuracy"] * 100, 2
            )
        }
        for name, value in results.items()
    }

    with open(benchmark_path, "w") as f:
        json.dump(benchmark_percentages, f, indent=2)

    print("\n" + "=" * 55)
    print("FINAL MODEL")
    print("=" * 55)

    print("Selected model:", selected_name)
    print(f"Training accuracy: {train_acc * 100:.2f}%")
    print(f"Test accuracy: {test_acc * 100:.2f}%")
    print(f"Weighted F1: {weighted_f1 * 100:.2f}%")
    print(
        f"95% CI: "
        f"{max(0, test_acc-half_width)*100:.2f}% - "
        f"{min(1, test_acc+half_width)*100:.2f}%"
    )

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nAll model comparisons:")
    for name, value in results.items():
        print(
            f"{name:28s} "
            f"CV: {value['cv_accuracy_mean']*100:.2f}% | "
            f"Test: {value['test_accuracy']*100:.2f}%"
        )

    print("\nSaved model:", model_path)
    print("Saved metadata:", metadata_path)

    return model_path, metadata_path


if __name__ == "__main__":
    train_and_save_model()
