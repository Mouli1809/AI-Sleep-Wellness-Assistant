def calculate_hydration_impact(hydration_liters, physical_activity_min):
    """
    Evaluates hydration level vs daily requirements based on activity level.
    Baseline requirement ~ 2.5L + activity compensation (0.5L per 60 min activity).
    """
    base_requirement = 2.5 + (physical_activity_min / 60.0) * 0.4
    percentage = (hydration_liters / base_requirement) * 100.0
    
    if percentage >= 90.0:
        status = "Optimal"
        badge_color = "#10B981"
        impact_msg = "Hydration supports deep REM cycles and cellular recovery."
    elif percentage >= 70.0:
        status = "Moderate Deficit"
        badge_color = "#F59E0B"
        impact_msg = "Mild dehydration may cause slight nighttime restlessness or dry throat."
    else:
        status = "Severe Deficit"
        badge_color = "#EF4444"
        impact_msg = "Low hydration elevates morning heart rate and degrades sleep recovery efficiency."
        
    return {
        "status": status,
        "percentage": round(min(150.0, percentage), 1),
        "requirement_liters": round(base_requirement, 1),
        "actual_liters": hydration_liters,
        "badge_color": badge_color,
        "impact_msg": impact_msg
    }
