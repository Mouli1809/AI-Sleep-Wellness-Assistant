import streamlit as st
import pandas as pd
from database.database import get_all_logs, delete_log, seed_sample_history_if_empty
from utils.helpers import format_hour_to_time_str

def render():
    st.title("📜 Sleep History & Logs")
    st.caption("Review past sleep records, metrics, and manage historical data entries.")
    
    seed_sample_history_if_empty()
    df = get_all_logs()
    
    if df.empty:
        st.info("No sleep logs recorded yet. Visit **Daily Check-In** to log your first sleep record.")
        return
        
    st.subheader(f"Total Logged Records: {len(df)}")
    
    # Search / Filter by Date
    search_term = st.text_input("🔍 Search by Date (YYYY-MM-DD) or Quality", value="")
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df["log_date"].astype(str).str.contains(search_term, case=False) |
            filtered_df["predicted_quality"].astype(str).str.contains(search_term, case=False)
        ]
        
    # Table View
    display_cols = [
        "id", "log_date", "sleep_duration", "bedtime_hour", "wake_hour", 
        "stress_level", "screen_time", "predicted_quality", "sleep_score", "recovery_score"
    ]
    
    view_df = filtered_df[display_cols].copy()
    view_df["bedtime_hour"] = view_df["bedtime_hour"].apply(format_hour_to_time_str)
    view_df["wake_hour"] = view_df["wake_hour"].apply(format_hour_to_time_str)
    
    view_df.columns = [
        "ID", "Date", "Duration (hrs)", "Bedtime", "Wake Time", 
        "Stress (1-10)", "Screen Time (min)", "ML Quality", "Sleep Score", "Recovery Score"
    ]
    
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    
    # Export Options
    st.markdown("### 📥 Data Export Options")
    ec1, ec2 = st.columns(2)
    with ec1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Export Logs as CSV",
            data=csv_data,
            file_name="sleep_wellness_logs.csv",
            mime="text/csv",
            use_container_width=True
        )
    with ec2:
        json_data = filtered_df.to_json(orient="records", indent=2).encode('utf-8')
        st.download_button(
            label="📦 Export Logs as JSON",
            data=json_data,
            file_name="sleep_wellness_logs.json",
            mime="application/json",
            use_container_width=True
        )
        
    st.markdown("---")
    
    # Log Inspection & Deletion Control
    st.subheader("🔍 Record Details & Management")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        log_ids = df["id"].tolist()
        log_date_labels = [f"ID {row['id']} — {row['log_date']} ({row['predicted_quality']})" for _, row in df.iterrows()]
        selected_idx = st.selectbox("Select Log Entry to Inspect", range(len(log_ids)), format_func=lambda i: log_date_labels[i])
        
        selected_row = df.iloc[selected_idx]
        with st.expander("📋 Detailed Telemetry Inspector", expanded=True):
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.write(f"**Log Date:** {selected_row['log_date']}")
                st.write(f"**Sleep Duration:** {selected_row['sleep_duration']} hrs")
                st.write(f"**Bedtime:** {format_hour_to_time_str(selected_row['bedtime_hour'])}")
                st.write(f"**Wake Time:** {format_hour_to_time_str(selected_row['wake_hour'])}")
            with ic2:
                st.write(f"**Stress Level:** {selected_row['stress_level']}/10")
                st.write(f"**Screen Time:** {selected_row['screen_time']} mins")
                st.write(f"**Physical Activity:** {selected_row['physical_activity']} mins")
                st.write(f"**Hydration:** {selected_row['hydration']} L ({selected_row['hydration_status']})")
            with ic3:
                st.write(f"**Noise Level:** {selected_row['noise_level']}/10")
                st.write(f"**Temperature:** {selected_row['temperature_comfort']}/10")
                st.write(f"**Light Level:** {selected_row['light_level']}/10")
                st.write(f"**Bed Comfort:** {selected_row['bed_comfort']}/10")
                
            if selected_row.get("notes"):
                st.info(f"**User Notes:** {selected_row['notes']}")
                
    with c2:
        st.markdown("### Delete Entry")
        st.caption("Remove selected record permanently from SQLite database.")
        if st.button("🗑️ Delete Selected Log", type="primary", use_container_width=True):
            del_id = int(selected_row["id"])
            delete_log(del_id)
            st.success(f"Deleted record ID {del_id}. Reloading...")
            st.rerun()

if __name__ == "__main__":
    from utils.helpers import inject_custom_css
    from database.database import init_db
    init_db()
    inject_custom_css()
    render()
