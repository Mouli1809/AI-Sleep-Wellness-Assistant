
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("data/sleep_dataset.csv")

X = df.drop(columns=["sleep_quality"])
y = df["sleep_quality"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = joblib.load("model/sleep_model_8660_backup.pkl")

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)
confidence = probabilities.max(axis=1)

print("\nSELECTIVE PREDICTION ANALYSIS")
print("Original test records:", len(y_test))
print("Original accuracy:", round(
    accuracy_score(y_test, predictions) * 100, 2
), "%")

for threshold in [0.60, 0.70, 0.80, 0.90, 0.95]:
    selected = confidence >= threshold

    if selected.sum() == 0:
        continue

    accuracy = accuracy_score(
        y_test.to_numpy()[selected],
        predictions[selected]
    )

    coverage = selected.mean() * 100

    print(
        f"\nThreshold: {threshold:.0%}",
        f"\nAccepted predictions: {selected.sum()}",
        f"\nCoverage: {coverage:.2f}%",
        f"\nAccuracy among accepted: {accuracy * 100:.2f}%"
    )

print("\nCOMPLETED")
