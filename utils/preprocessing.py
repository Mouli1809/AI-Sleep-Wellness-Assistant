import pandas as pd
import numpy as np

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

def format_input_features(
    sleep_duration,
    bedtime_hour,
    wake_hour,
    previous_sleep_duration,
    stress_level,
    physical_activity,
    hydration,
    screen_time,
    noise_level,
    temperature_comfort,
    light_level,
    bed_comfort
):
    """
    Constructs a DataFrame matching the model's feature column signature.
    """
    input_dict = {
        "sleep_duration": float(sleep_duration),
        "bedtime_hour": float(bedtime_hour),
        "wake_hour": float(wake_hour),
        "previous_sleep_duration": float(previous_sleep_duration),
        "stress_level": int(stress_level),
        "physical_activity": int(physical_activity),
        "hydration": float(hydration),
        "screen_time": int(screen_time),
        "noise_level": int(noise_level),
        "temperature_comfort": int(temperature_comfort),
        "light_level": int(light_level),
        "bed_comfort": int(bed_comfort)
    }
    
    df = pd.DataFrame([input_dict], columns=FEATURE_COLUMNS)
    return df

def validate_input_ranges(log_data):
    """
    Ensures input parameters fall within realistic physical limits.
    """
    errors = []
    if log_data["sleep_duration"] < 1.0 or log_data["sleep_duration"] > 16.0:
        errors.append("Sleep duration must be between 1 and 16 hours.")
    if log_data["hydration"] < 0.0 or log_data["hydration"] > 10.0:
        errors.append("Hydration must be between 0 and 10 liters.")
    if log_data["physical_activity"] < 0 or log_data["physical_activity"] > 600:
        errors.append("Physical activity must be between 0 and 600 minutes.")
    return errors
