import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "database", "sleep_wellness.db")

def get_db_connection(db_path=DEFAULT_DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        sleep_duration REAL NOT NULL,
        bedtime_hour REAL NOT NULL,
        wake_hour REAL NOT NULL,
        previous_sleep_duration REAL NOT NULL,
        stress_level INTEGER NOT NULL,
        physical_activity INTEGER NOT NULL,
        hydration REAL NOT NULL,
        screen_time INTEGER NOT NULL,
        noise_level INTEGER NOT NULL,
        temperature_comfort INTEGER NOT NULL,
        light_level INTEGER NOT NULL,
        bed_comfort INTEGER NOT NULL,
        predicted_quality TEXT NOT NULL,
        sleep_score REAL NOT NULL,
        sleep_debt REAL NOT NULL,
        consistency_score REAL NOT NULL,
        environment_score REAL NOT NULL,
        hydration_status TEXT NOT NULL,
        recovery_score REAL NOT NULL,
        notes TEXT
    );
    """)
    conn.commit()
    conn.close()

def insert_log(log_data, db_path=DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    sql = """
    INSERT INTO daily_logs (
        log_date, created_at, sleep_duration, bedtime_hour, wake_hour,
        previous_sleep_duration, stress_level, physical_activity, hydration,
        screen_time, noise_level, temperature_comfort, light_level, bed_comfort,
        predicted_quality, sleep_score, sleep_debt, consistency_score,
        environment_score, hydration_status, recovery_score, notes
    ) VALUES (
        :log_date, :created_at, :sleep_duration, :bedtime_hour, :wake_hour,
        :previous_sleep_duration, :stress_level, :physical_activity, :hydration,
        :screen_time, :noise_level, :temperature_comfort, :light_level, :bed_comfort,
        :predicted_quality, :sleep_score, :sleep_debt, :consistency_score,
        :environment_score, :hydration_status, :recovery_score, :notes
    )
    ON CONFLICT(log_date) DO UPDATE SET
        created_at = excluded.created_at,
        sleep_duration = excluded.sleep_duration,
        bedtime_hour = excluded.bedtime_hour,
        wake_hour = excluded.wake_hour,
        previous_sleep_duration = excluded.previous_sleep_duration,
        stress_level = excluded.stress_level,
        physical_activity = excluded.physical_activity,
        hydration = excluded.hydration,
        screen_time = excluded.screen_time,
        noise_level = excluded.noise_level,
        temperature_comfort = excluded.temperature_comfort,
        light_level = excluded.light_level,
        bed_comfort = excluded.bed_comfort,
        predicted_quality = excluded.predicted_quality,
        sleep_score = excluded.sleep_score,
        sleep_debt = excluded.sleep_debt,
        consistency_score = excluded.consistency_score,
        environment_score = excluded.environment_score,
        hydration_status = excluded.hydration_status,
        recovery_score = excluded.recovery_score,
        notes = excluded.notes;
    """
    
    if "created_at" not in log_data or not log_data["created_at"]:
        log_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "notes" not in log_data:
        log_data["notes"] = ""

    cursor.execute(sql, log_data)
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_all_logs(db_path=DEFAULT_DB_PATH):
    init_db(db_path)
    conn = get_db_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM daily_logs ORDER BY log_date DESC", conn)
    conn.close()
    return df

def get_recent_logs(limit=7, db_path=DEFAULT_DB_PATH):
    init_db(db_path)
    conn = get_db_connection(db_path)
    df = pd.read_sql_query(f"SELECT * FROM daily_logs ORDER BY log_date DESC LIMIT {int(limit)}", conn)
    conn.close()
    return df

def delete_log(log_id, db_path=DEFAULT_DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

def get_dashboard_metrics(db_path=DEFAULT_DB_PATH):
    df = get_all_logs(db_path)
    if df.empty:
        return None
    
    latest = df.iloc[0]
    avg_duration = round(df["sleep_duration"].mean(), 1)
    avg_score = round(df["sleep_score"].mean(), 1)
    avg_recovery = round(df["recovery_score"].mean(), 1)
    total_logs = len(df)
    
    return {
        "latest": latest,
        "avg_duration": avg_duration,
        "avg_score": avg_score,
        "avg_recovery": avg_recovery,
        "total_logs": total_logs,
        "history_df": df
    }

def seed_sample_history_if_empty(db_path=DEFAULT_DB_PATH):
    init_db(db_path)
    df = get_all_logs(db_path)
    if len(df) > 0:
        return
    
    # Imports inside function to prevent circular dependency
    from modules.sleep_score import calculate_sleep_score
    from modules.sleep_debt import calculate_sleep_debt
    from modules.consistency import calculate_consistency_score
    from modules.environment import calculate_environment_score
    from modules.hydration import calculate_hydration_impact
    from modules.recovery import calculate_recovery_score
    
    today = datetime.now().date()
    sample_entries = [
        {"days_ago": 6, "duration": 6.0, "bedtime": 23.5, "wake": 5.5, "prev": 6.2, "stress": 7, "act": 30, "hyd": 1.8, "screen": 90, "noise": 6, "temp": 5, "light": 6, "bed": 6, "pred": "Average"},
        {"days_ago": 5, "duration": 7.0, "bedtime": 23.0, "wake": 6.0, "prev": 6.0, "stress": 6, "act": 45, "hyd": 2.2, "screen": 60, "noise": 4, "temp": 7, "light": 4, "bed": 7, "pred": "Average"},
        {"days_ago": 4, "duration": 5.5, "bedtime": 0.5, "wake": 6.0, "prev": 7.0, "stress": 8, "act": 15, "hyd": 1.5, "screen": 120, "noise": 7, "temp": 4, "light": 7, "bed": 5, "pred": "Poor"},
        {"days_ago": 3, "duration": 8.0, "bedtime": 22.5, "wake": 6.5, "prev": 5.5, "stress": 4, "act": 60, "hyd": 2.8, "screen": 30, "noise": 2, "temp": 9, "light": 2, "bed": 9, "pred": "Good"},
        {"days_ago": 2, "duration": 7.5, "bedtime": 22.8, "wake": 6.3, "prev": 8.0, "stress": 3, "act": 50, "hyd": 2.5, "screen": 40, "noise": 3, "temp": 8, "light": 3, "bed": 8, "pred": "Good"},
        {"days_ago": 1, "duration": 8.2, "bedtime": 22.2, "wake": 6.4, "prev": 7.5, "stress": 2, "act": 75, "hyd": 3.0, "screen": 20, "noise": 2, "temp": 9, "light": 2, "bed": 9, "pred": "Good"},
        {"days_ago": 0, "duration": 7.8, "bedtime": 22.5, "wake": 6.3, "prev": 8.2, "stress": 3, "act": 60, "hyd": 2.7, "screen": 25, "noise": 2, "temp": 8, "light": 2, "bed": 9, "pred": "Good"},
    ]
    
    durations = [e["duration"] for e in sample_entries]
    bedtimes = [e["bedtime"] for e in sample_entries]
    waketimes = [e["wake"] for e in sample_entries]
    
    for i, entry in enumerate(sample_entries):
        entry_date = (today - timedelta(days=entry["days_ago"])).strftime("%Y-%m-%d")
        history_so_far = sample_entries[:i+1]
        history_durations = [h["duration"] for h in history_so_far]
        history_bedtimes = [h["bedtime"] for h in history_so_far]
        history_waketimes = [h["wake"] for h in history_so_far]
        
        s_score = calculate_sleep_score(entry["duration"], entry["stress"], entry["screen"], entry["noise"], entry["temp"], entry["light"], entry["bed"])
        s_debt = calculate_sleep_debt(history_durations)
        c_score = calculate_consistency_score(history_bedtimes, history_waketimes)
        e_score = calculate_environment_score(entry["noise"], entry["temp"], entry["light"], entry["bed"])
        h_info = calculate_hydration_impact(entry["hyd"], entry["act"])
        r_score = calculate_recovery_score(entry["duration"], entry["prev"], entry["stress"], entry["act"])
        
        log_data = {
            "log_date": entry_date,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sleep_duration": entry["duration"],
            "bedtime_hour": entry["bedtime"],
            "wake_hour": entry["wake"],
            "previous_sleep_duration": entry["prev"],
            "stress_level": entry["stress"],
            "physical_activity": entry["act"],
            "hydration": entry["hyd"],
            "screen_time": entry["screen"],
            "noise_level": entry["noise"],
            "temperature_comfort": entry["temp"],
            "light_level": entry["light"],
            "bed_comfort": entry["bed"],
            "predicted_quality": entry["pred"],
            "sleep_score": s_score,
            "sleep_debt": s_debt,
            "consistency_score": c_score,
            "environment_score": e_score,
            "hydration_status": h_info["status"],
            "recovery_score": r_score,
            "notes": "Sample initial log entry"
        }
        insert_log(log_data, db_path)

if __name__ == "__main__":
    init_db()
    seed_sample_history_if_empty()
    print("Database initialized & sample history seeded.")
