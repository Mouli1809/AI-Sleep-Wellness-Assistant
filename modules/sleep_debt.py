import numpy as np

def calculate_sleep_debt(recent_durations, baseline_target=8.0):
    """
    Calculates accumulated sleep debt over recent days (up to 7 days).
    Positive debt = sleep deficit (hours missed).
    Negative debt = sleep surplus.
    """
    if not recent_durations:
        return 0.0
    
    # Take at most last 7 entries
    durations = recent_durations[:7]
    deficits = [baseline_target - d for d in durations]
    
    # Weighted recent debt (more recent days have slightly higher weight)
    weights = np.linspace(1.2, 0.8, len(deficits))
    weighted_debt = np.sum(np.array(deficits) * weights) / np.sum(weights) * len(deficits)
    
    return round(float(weighted_debt), 1)

def get_sleep_debt_status(debt_hours):
    if debt_hours <= -1.0:
        return {"status": "Surplus", "color": "#10B981", "badge": "Fully Rested"}
    elif debt_hours <= 1.5:
        return {"status": "Minimal", "color": "#3B82F6", "badge": "Optimal Balance"}
    elif debt_hours <= 4.0:
        return {"status": "Moderate", "color": "#F59E0B", "badge": "Mild Fatigue"}
    else:
        return {"status": "Severe", "color": "#EF4444", "badge": "High Sleep Debt"}
