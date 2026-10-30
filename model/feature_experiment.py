
import os
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    RandomForestRegressor
)
from sklearn.metrics import accuracy_score, f1_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(
    PROJECT_DIR, "data", "sleep_dataset.csv"
)

df = pd.read_csv(DATA_PATH)

# Original features
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

# Feature engineering
def create_features(data):

    data = data.copy()

    data["duration_deviation"] = abs(
        data["sleep_duration"] - 8.0
    )

    data["previous_sleep_debt"] = np.maximum(
        0, 8.0 - data["previous_sleep_duration"]
    )

    data["environment_comfort"] = (
        (11 - data["noise_level"])
        + data["temperature_comfort"]
        + (11 - data["light_level"])
        + data["bed_comfort"]
    )

    data["stress_sleep_interaction"] = (
        data["stress_level"] * data["duration_deviation"]
    )

    data["screen_stress_interaction"] = (
        data["screen_time"] * data["stress_level"]
    )

    data["sleep_schedule_difference"] = (
        data["bedtime_hour"] - 22.0
    ) % 24

    return data


X = create_features(df[FEATURE_COLUMNS])
y = df["sleep_quality"].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

models = {
    "Extra Trees": ExtraTreesClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=1,
        max_features=0.8,
        random_state=42,
        n_jobs=-1
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=1,
        max_features=0.8,
        random_state=42,
        n_jobs=-1
    ),

    "HistGradientBoosting": HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=20,
        min_samples_leaf=15,
        random_state=42
    )
}

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

print("\nFEATURE ENGINEERING EXPERIMENT")
print("=" * 55)
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Total features:", X.shape[1])

for name, classifier in models.items():

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", classifier)
    ])

    scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="accuracy",
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    prediction = model.predict(X_test)

    accuracy = accuracy_score(y_test, prediction)
    f1 = f1_score(
        y_test,
        prediction,
        average="weighted"
    )

    print("\nModel:", name)
    print(f"CV Accuracy: {scores.mean()*100:.2f}%")
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    print(f"Weighted F1: {f1*100:.2f}%")

print("\nExperiment completed.")
