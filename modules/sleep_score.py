def calculate_sleep_score(sleep_duration, stress_level, screen_time, noise_level, temp_comfort, light_level, bed_comfort):
    """
    Calculates a composite 0-100 Sleep Wellness Score.
    - Sleep Duration (Ideal 7.5 - 8.5 hours): up to 45 pts
    - Stress Level (1-10): up to -20 pts penalty
    - Screen Time (0-180 min): up to -15 pts penalty
    - Environment Comfort (Noise, Temp, Light, Bed): up to 30 pts
    """
    # 1. Duration score (max 45)
    ideal = 8.0
    diff = abs(sleep_duration - ideal)
    if diff <= 0.5:
        duration_pts = 45.0
    elif diff <= 1.5:
        duration_pts = 45.0 - (diff - 0.5) * 12.0
    elif diff <= 3.0:
        duration_pts = 33.0 - (diff - 1.5) * 15.0
    else:
        duration_pts = max(5.0, 10.0 - (diff - 3.0) * 4.0)
        
    # 2. Stress penalty (1=min, 10=max)
    stress_penalty = (stress_level - 1) * 2.0  # 0 to 18 pts penalty
    
    # 3. Screen time penalty
    screen_penalty = min(15.0, (screen_time / 15.0) * 1.25) # 0 to 15 pts penalty
    
    # 4. Environment score (max 30)
    # Noise: 1 best, 10 worst -> score (11-noise)
    # Light: 1 best, 10 worst -> score (11-light)
    env_sum = (11 - noise_level) + temp_comfort + (11 - light_level) + bed_comfort # max 40
    env_pts = (env_sum / 40.0) * 30.0
    
    total = duration_pts - stress_penalty - screen_penalty + env_pts
    final_score = round(max(0.0, min(100.0, total)), 1)
    return final_score
