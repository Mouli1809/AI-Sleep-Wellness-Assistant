
import numpy as np
import pandas as pd

df = pd.read_csv("data/sleep_dataset.csv")

# Recalculate the original score
duration_score = 100 - abs(df["sleep_duration"] - 8.0) * 17
previous_score = 100 - abs(df["previous_sleep_duration"] - 8.0) * 7

stress_penalty = df["stress_level"] * 4.5
screen_penalty = df["screen_time"] * 0.16

bedtime_penalty = np.maximum(
    0, df["bedtime_hour"] - 23
) * 2.0

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

# Noise cannot be recovered from the CSV.
# Therefore this is the score before random noise.
df["score_before_noise"] = score

print("\nLABEL DISTRIBUTION")
print(df["sleep_quality"].value_counts())

print("\nDISTANCE FROM CLASS BOUNDARIES")
for boundary in [20, 38]:
    close = (abs(score - boundary) <= 3).sum()
    print(f"Within 3 points of {boundary}: {close} records")

print("\nSCORE SUMMARY")
print(df.groupby("sleep_quality")["score_before_noise"].agg(
    ["count", "mean", "min", "max"]
))

print("\nAnalysis completed.")
