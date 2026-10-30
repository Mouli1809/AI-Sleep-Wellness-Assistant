
import pandas as pd
import numpy as np
import os


def generate_sleep_dataset(num_rows=5000, random_seed=42):
    rng = np.random.default_rng(random_seed)

    # 1. Generate input features
    sleep_duration = np.round(
        np.clip(rng.normal(7.2, 1.8, num_rows), 2.0, 14.0), 1
    )

    bedtime_hour = np.round(rng.uniform(21.0, 26.5, num_rows) % 24, 1)
    wake_hour = np.round((bedtime_hour + sleep_duration) % 24, 1)

    previous_sleep_duration = np.round(
        np.clip(rng.normal(7.1, 1.5, num_rows), 2.0, 14.0), 1
    )

    stress_level = rng.integers(1, 11, num_rows)
    physical_activity = rng.integers(0, 121, num_rows)
    hydration = np.round(rng.uniform(0.5, 4.0, num_rows), 1)
    screen_time = rng.integers(0, 181, num_rows)

    noise_level = rng.integers(1, 11, num_rows)
    temperature_comfort = rng.integers(1, 11, num_rows)
    light_level = rng.integers(1, 11, num_rows)
    bed_comfort = rng.integers(1, 11, num_rows)

    # 2. Calculate sleep wellness score
    duration_score = 100 - np.abs(sleep_duration - 8.0) * 17
    previous_score = 100 - np.abs(previous_sleep_duration - 8.0) * 7

    stress_penalty = stress_level * 4.5
    screen_penalty = screen_time * 0.16

    bedtime_penalty = np.where(
        bedtime_hour >= 24,
        (bedtime_hour - 24) * 2.0,
        np.maximum(0, bedtime_hour - 23) * 2.0
    )

    environment_score = (
        (11 - noise_level) * 2.0
        + temperature_comfort * 2.0
        + (11 - light_level) * 2.0
        + bed_comfort * 2.0
    )

    activity_bonus = np.minimum(12, physical_activity * 0.1)
    hydration_bonus = np.minimum(8, hydration * 2.0)

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

    # Penalize unusually short or long sleep
    score -= np.where(sleep_duration < 4.0, 30, 0)
    score -= np.where(sleep_duration > 10.0, 25, 0)

    # Small random variation
    score += rng.normal(0, 3, num_rows)

    # 3. Assign target classes
    labels = np.where(
    score >= 38, "Good",
    np.where(score >= 20, "Average", "Poor")
)
    df = pd.DataFrame({
        "sleep_duration": sleep_duration,
        "bedtime_hour": bedtime_hour,
        "wake_hour": wake_hour,
        "previous_sleep_duration": previous_sleep_duration,
        "stress_level": stress_level,
        "physical_activity": physical_activity,
        "hydration": hydration,
        "screen_time": screen_time,
        "noise_level": noise_level,
        "temperature_comfort": temperature_comfort,
        "light_level": light_level,
        "bed_comfort": bed_comfort,
        "sleep_quality": labels
    })

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "sleep_dataset.csv")
    df.to_csv(csv_path, index=False)

    print("Dataset generated successfully!")
    print("Records:", len(df))
    print("Columns:", len(df.columns))
    print("\nClass distribution:")
    print(df["sleep_quality"].value_counts())
    print("\nSleep duration range:")
    print(df["sleep_duration"].min(), "to", df["sleep_duration"].max())

    return csv_path


if __name__ == "__main__":
    generate_sleep_dataset()
