def calculate_environment_score(noise_level, temp_comfort, light_level, bed_comfort):
    """
    Calculates 0-100 Environmental Comfort Index.
    - noise_level (1 quiet - 10 loud): 25%
    - temp_comfort (1 uncomfortable - 10 optimal): 25%
    - light_level (1 dark - 10 bright): 25%
    - bed_comfort (1 poor - 10 excellent): 25%
    """
    noise_score = (11 - noise_level) * 10.0
    temp_score = temp_comfort * 10.0
    light_score = (11 - light_level) * 10.0
    bed_score = bed_comfort * 10.0
    
    total = (noise_score + temp_score + light_score + bed_score) / 4.0
    return round(max(0.0, min(100.0, total)), 1)

def get_environment_breakdown(noise_level, temp_comfort, light_level, bed_comfort):
    return {
        "Noise Control": f"{11 - noise_level}/10",
        "Temperature": f"{temp_comfort}/10",
        "Darkness": f"{11 - light_level}/10",
        "Bed Comfort": f"{bed_comfort}/10"
    }
