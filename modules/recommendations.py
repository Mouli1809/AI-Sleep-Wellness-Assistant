def generate_recommendations(log_data):
    """
    Generates rule-based actionable recommendations + a structured daily action plan.
    """
    recs = []
    daily_plan = []
    
    sleep_dur = log_data.get("sleep_duration", 7.5)
    stress = log_data.get("stress_level", 5)
    screen = log_data.get("screen_time", 60)
    noise = log_data.get("noise_level", 4)
    temp = log_data.get("temperature_comfort", 7)
    light = log_data.get("light_level", 3)
    hyd = log_data.get("hydration", 2.0)
    act = log_data.get("physical_activity", 30)
    predicted_quality = log_data.get("predicted_quality", "Average")
    
    # 1. Screen Time & Digital Hygiene
    if screen > 45:
        recs.append({
            "category": "Digital Hygiene",
            "icon": "📱",
            "title": "High Pre-Bed Screen Time",
            "detail": f"You logged {screen} mins of screen exposure before bed. Blue light suppresses melatonin synthesis.",
            "action": "Enable Night Shift / Warm Filter after 9:00 PM and cut screens completely 30 minutes before sleep."
        })
        daily_plan.append("9:30 PM: Turn off TV, laptop, and smartphone displays.")
    
    # 2. Stress & Nervous System Modulation
    if stress >= 6:
        recs.append({
            "category": "Stress Management",
            "icon": "🧘",
            "title": "Elevated Cortisol Risk",
            "detail": f"Stress level is {stress}/10. High evening cortisol causes micro-arousals during slow-wave sleep.",
            "action": "Practice 5 minutes of 4-7-8 box breathing or progressive muscle relaxation in bed."
        })
        daily_plan.append("9:45 PM: 5-minute deep diaphragmatic 4-7-8 breathing exercise.")
    
    # 3. Environment Adjustments
    if noise >= 6 or light >= 5 or temp <= 5:
        env_details = []
        if noise >= 6: env_details.append("high ambient noise")
        if light >= 5: env_details.append("excess ambient light")
        if temp <= 5: env_details.append("sub-optimal temperature")
        
        recs.append({
            "category": "Environment",
            "icon": "🌙",
            "title": "Sleep Sanctuary Optimization",
            "detail": f"Room environment compromised by {', '.join(env_details)}.",
            "action": "Utilize earplugs/white noise machine, blackout curtains, and aim for a room temperature between 18°C–20°C (65°F–68°F)."
        })
        daily_plan.append("10:00 PM: Adjust thermostat to ~19°C and draw blackout curtains.")
        
    # 4. Hydration & Physical Activity
    if hyd < 2.0:
        recs.append({
            "category": "Hydration",
            "icon": "💧",
            "title": "Hydration Target Deficit",
            "detail": f"Log shows only {hyd}L of water. Dehydration causes nighttime throat dryness and muscle cramps.",
            "action": "Drink 500ml water upon waking tomorrow and maintain steady intake until 2 hours before bedtime."
        })
        daily_plan.append("Morning (Wakeup): Hydrate immediately with 500ml room-temperature water.")
        
    # 5. Sleep Duration Target
    if sleep_dur < 7.0:
        recs.append({
            "category": "Duration",
            "icon": "⏰",
            "title": "Sub-optimal Sleep Duration",
            "detail": f"Logged {sleep_dur} hrs (ideal is 7.5 - 8.5 hrs). Accumulated sleep debt degrades cognitive focus.",
            "action": "Shift tonight's bedtime 30 minutes earlier to assist physiological catch-up."
        })
        daily_plan.append("10:15 PM: Get into bed to allow a 15-minute wind-down buffer before target sleep.")
    else:
        daily_plan.append("10:30 PM: Lights out for target 8-hour sleep window.")

    if not recs:
        recs.append({
            "category": "Maintenance",
            "icon": "🌟",
            "title": "Excellent Sleep Dynamics",
            "detail": "Your sleep factors are well balanced across environment, stress, and habits.",
            "action": "Maintain your current evening wind-down routine and wake times."
        })

    return {
        "recommendations": recs,
        "daily_plan": daily_plan,
        "overall_summary": f"Predicted Quality: {predicted_quality}. " + ("Focus on evening wind-down." if predicted_quality != "Good" else "Great work maintaining optimal sleep environment!")
    }
