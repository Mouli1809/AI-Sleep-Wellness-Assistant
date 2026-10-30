
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split

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

results = pd.DataFrame({
    "Actual": y_test.to_numpy(),
    "Predicted": predictions,
    "Confidence": confidence
})

results["Correct"] = (
    results["Actual"] == results["Predicted"]
)

print("\nCONFIDENCE ANALYSIS")

print("\nCorrect predictions:")
print(
    results.loc[results["Correct"], "Confidence"]
    .describe().round(3)
)

print("\nIncorrect predictions:")
print(
    results.loc[~results["Correct"], "Confidence"]
    .describe().round(3)
)

print("\nCONFIDENCE GROUPS")

results["Confidence_Group"] = pd.cut(
    results["Confidence"],
    bins=[0, 0.60, 0.80, 0.90, 1.001],
    labels=["Below 60%", "60-80%", "80-90%", "90-100%"]
)

print(pd.crosstab(
    results["Confidence_Group"],
    results["Correct"]
))

print("\nCOMPLETED")
