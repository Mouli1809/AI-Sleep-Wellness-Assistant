def calculate_recovery_score(sleep_duration, previous_sleep_duration, stress_level, physical_activity):
    """
    Calculates physical & nervous system recovery readiness (0-100).
    Combines sleep duration, sleep continuity (previous duration), stress recovery, and activity load balance.
    """
    # 1. Sleep adequacy (40 pts max)
    avg_sleep = (sleep_duration * 0.6) + (previous_sleep_duration * 0.4)
    sleep_pts = min(40.0, (avg_sleep / 8.0) * 40.0)
    
    # 2. Stress relief (30 pts max)
    stress_pts = (11 - stress_level) * 3.0
    
    # 3. Activity load balance (30 pts max)
    # 30 - 60 min is optimal (30 pts), 0 min = 15 pts, >90 min without rest = 20 pts
    if 30 <= physical_activity <= 75:
        act_pts = 30.0
    elif physical_activity < 30:
        act_pts = 15.0 + (physical_activity / 30.0) * 15.0
    else:
        act_pts = max(10.0, 30.0 - (physical_activity - 75) * 0.3)
        
    total = sleep_pts + stress_pts + act_pts
    return round(max(0.0, min(100.0, total)), 1)
