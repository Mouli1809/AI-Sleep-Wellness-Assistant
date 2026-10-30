
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

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

print("\nCONFUSION MATRIX")
print(confusion_matrix(
    y_test,
    predictions,
    labels=["Poor", "Average", "Good"]
))

print("\nCLASSIFICATION REPORT")
print(classification_report(y_test, predictions))

errors = X_test.copy()
errors["Actual"] = y_test
errors["Predicted"] = predictions

wrong = errors[errors["Actual"] != errors["Predicted"]]

print("\nTOTAL INCORRECT PREDICTIONS:", len(wrong))

print("\nERRORS BY ACTUAL CLASS")
print(wrong["Actual"].value_counts())

print("\nACTUAL VS PREDICTED")
print(pd.crosstab(wrong["Actual"], wrong["Predicted"]))

print("\nERROR ANALYSIS COMPLETED")
