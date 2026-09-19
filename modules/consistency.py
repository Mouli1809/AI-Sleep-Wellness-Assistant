import numpy as np

def calculate_consistency_score(bedtimes, waketimes):
    """
    Calculates 0-100 Bedtime/Wake-time Consistency Score.
    Low variance = High Score (100).
    High variance = Low Score.
    """
    if not bedtimes or len(bedtimes) < 2:
        return 85.0 # Default for single/initial entry
    
    # Normalize bedtimes so midnight wrap-around is smooth (e.g., 23.5 vs 0.5)
    norm_bedtimes = []
    for b in bedtimes:
        if b < 12.0:
            norm_bedtimes.append(b + 24.0)
        else:
            norm_bedtimes.append(b)
            
    bed_std = np.std(norm_bedtimes)
    wake_std = np.std(waketimes)
    
    # Variance penalty: std of 0.5h (~30 mins) is great, std of 2h is poor
    combined_std = (bed_std + wake_std) / 2.0
    
    score = 100.0 - (combined_std * 35.0)
    return round(max(0.0, min(100.0, score)), 1)
