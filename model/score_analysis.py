
import pandas as pd
import numpy as np

df = pd.read_csv("data/sleep_dataset.csv")

duration_score = 100 - abs(df["sleep_duration"] - 8) * 17
previous_score = 100 - abs(df["previous_sleep_duration"] - 8) * 7

stress_penalty = df["stress_level"] * 4.5
screen_penalty = df["screen_time"] * 0.16

bedtime_penalty = np.maximum(
    0, df["bedtime_hour"] - 23
) * 2

environment_score = (
    (11 - df["noise_level"]) * 2
    + df["temperature_comfort"] * 2
    + (11 - df["light_level"]) * 2
    + df["bed_comfort"] * 2
)

activity_bonus = np.minimum(12, df["physical_activity"] * 0.1)
hydration_bonus = np.minimum(8, df["hydration"] * 2)

score = (
    duration_score * 0.45
    + previous_score * 0.10
    - stress_penalty * 0.75
    - screen_penalty * 0.90
    + environment_score * 0.20
    + activity_bonus
    + hydration_bonus
    - bedtime_penalty
)

score -= np.where(df["sleep_duration"] < 4, 30, 0)
score -= np.where(df["sleep_duration"] > 10, 25, 0)

df["estimated_score"] = score

print("\nAVERAGE SCORE BY CLASS")
print(df.groupby("sleep_quality")["estimated_score"].agg(
    ["mean", "std", "min", "max"]
).round(2))

print("\nCLASS OVERLAP CHECK")

for label in ["Poor", "Average", "Good"]:
    values = df.loc[
        df["sleep_quality"] == label, "estimated_score"
    ]

    print(
        label,
        "| 10th percentile:", round(values.quantile(0.10), 2),
        "| Median:", round(values.median(), 2),
        "| 90th percentile:", round(values.quantile(0.90), 2)
    )

print("\nCOMPLETED")

