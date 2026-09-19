import pandas as pd
import numpy as np
import os

def generate_sleep_dataset(num_rows=1500, random_seed=42):
    np.random.seed(random_seed)
    
    # 1. Feature generation
    sleep_duration = np.round(np.random.normal(loc=7.2, scale=1.3, size=num_rows), 1)
    sleep_duration = np.clip(sleep_duration, 4.0, 10.0)
    
    bedtime_hour = np.round(np.random.uniform(21.0, 26.5, size=num_rows) % 24, 1) # 21.0 (9 PM) to 2.5 (2:30 AM)
    wake_hour = np.round((bedtime_hour + sleep_duration) % 24, 1)
    
    previous_sleep_duration = np.round(np.random.normal(loc=7.1, scale=1.2, size=num_rows), 1)
    previous_sleep_duration = np.clip(previous_sleep_duration, 4.0, 10.0)
    
    stress_level = np.random.randint(1, 11, size=num_rows)
    physical_activity = np.random.randint(0, 121, size=num_rows) # minutes
    hydration = np.round(np.random.uniform(0.8, 4.0, size=num_rows), 1) # liters
    screen_time = np.random.randint(0, 181, size=num_rows) # minutes before bed
    
    noise_level = np.random.randint(1, 11, size=num_rows) # 1 quiet, 10 loud
    temperature_comfort = np.random.randint(1, 11, size=num_rows) # 1 uncomfortable, 10 ideal
    light_level = np.random.randint(1, 11, size=num_rows) # 1 dark, 10 bright
    bed_comfort = np.random.randint(1, 11, size=num_rows) # 1 bad, 10 great
    
    # 2. Derive target sleep_quality (Poor / Average / Good) with realistic physiological rules + noise
    quality_labels = []
    
    for i in range(num_rows):
        dur = sleep_duration[i]
        dur_score = 100 - abs(dur - 8.0) * 16.0
        
        stress_pen = stress_level[i] * 4.5
        screen_pen = (screen_time[i] / 60.0) * 8.0
        
        env_score = (
            (11 - noise_level[i]) * 2.5 +
            temperature_comfort[i] * 2.5 +
            (11 - light_level[i]) * 2.5 +
            bed_comfort[i] * 2.5
        ) # range ~ 10 to 100
        
        act_bonus = min(12.0, physical_activity[i] * 0.1)
        hyd_bonus = min(8.0, hydration[i] * 2.5)
        
        composite = dur_score - stress_pen - screen_pen + (env_score * 0.25) + act_bonus + hyd_bonus
        composite += np.random.normal(0, 5) # add realistic random variance
        
        if composite >= 74:
            quality_labels.append("Good")
        elif composite >= 52:
            quality_labels.append("Average")
        else:
            quality_labels.append("Poor")
            
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
        "sleep_quality": quality_labels
    })
    
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "sleep_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset created successfully with {len(df)} records at {csv_path}")
    print("Class distribution:\n", df["sleep_quality"].value_counts())
    return csv_path

if __name__ == "__main__":
    generate_sleep_dataset()
