import os
import joblib
import datetime
import streamlit as st
import pandas as pd

from database.database import insert_log, get_all_logs
from utils.preprocessing import format_input_features, validate_input_ranges
from modules.sleep_score import calculate_sleep_score
from modules.sleep_debt import calculate_sleep_debt
from modules.consistency import calculate_consistency_score
from modules.environment import calculate_environment_score
from modules.hydration import calculate_hydration_impact
from modules.recovery import calculate_recovery_score
from modules.recommendations import generate_recommendations
from utils.helpers import get_quality_badge_html, format_hour_to_time_str

MODEL_PATH = os.path.join("model", "sleep_model.pkl")

@st.cache_resource
def load_ml_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def render():
    st.title("📝 Daily Sleep Check-In")
    st.caption("Log your daily sleep factors to get an AI-assisted sleep-quality prediction and wellness metrics.")
    st.info("ℹ️ This is an educational wellness prototype using a synthetic dataset. It is not a medical diagnosis tool.")
    
    pipeline = load_ml_model()
    if pipeline is None:
        st.warning("⚠️ Trained ML model not found. Please train the model first by running `python model/train_model.py`.")
        
    with st.form("checkin_form", clear_on_submit=False):
        st.subheader("1. Sleep Timing & Duration")
        c1, c2, c3 = st.columns(3)
        with c1:
            log_date = st.date_input("Check-In Date", value=datetime.date.today())
            sleep_dur = st.number_input("Sleep Duration (Hours)", min_value=1.0, max_value=15.0, value=7.5, step=0.5)
        with c2:
            bedtime_val = st.slider("Bedtime Hour (24h format)", min_value=20.0, max_value=27.5, value=22.5, step=0.5,
                                    help="22.5 = 10:30 PM, 24.5 = 12:30 AM")
            bedtime_norm = bedtime_val % 24.0
            st.caption(f"Selected Bedtime: **{format_hour_to_time_str(bedtime_norm)}**")
        with c3:
            wake_val = st.slider("Wake-up Hour (24h format)", min_value=4.0, max_value=12.0, value=6.5, step=0.5)
            st.caption(f"Selected Wake-up: **{format_hour_to_time_str(wake_val)}**")
            
        prev_dur = st.number_input("Previous Night's Sleep Duration (Hours)", min_value=1.0, max_value=15.0, value=7.0, step=0.5)
        
        st.markdown("---")
        st.subheader("2. Daytime Lifestyle & Stress")
        l1, l2, l3, l4 = st.columns(4)
        with l1:
            stress = st.slider("Stress Level (1-10)", min_value=1, max_value=10, value=4)
        with l2:
            activity = st.number_input("Physical Activity (Minutes)", min_value=0, max_value=300, value=45, step=15)
        with l3:
            hydration = st.number_input("Water Hydration (Liters)", min_value=0.5, max_value=8.0, value=2.5, step=0.2)
        with l4:
            screen = st.number_input("Pre-Bed Screen Time (Minutes)", min_value=0, max_value=240, value=45, step=15)
            
        st.markdown("---")
        st.subheader("3. Bedroom Environment")
        e1, e2, e3, e4 = st.columns(4)
        with e1:
            noise = st.slider("Noise Level (1Quiet - 10Loud)", min_value=1, max_value=10, value=3)
        with e2:
            temp = st.slider("Temp Comfort (1Bad - 10Optimal)", min_value=1, max_value=10, value=8)
        with e3:
            light = st.slider("Light Level (1Dark - 10Bright)", min_value=1, max_value=10, value=2)
        with e4:
            bed = st.slider("Bed Comfort (1Bad - 10Great)", min_value=1, max_value=10, value=8)
            
        notes = st.text_input("Optional Daily Notes", value="")
        
        submit_btn = st.form_submit_button("🤖 Predict & Log Sleep Wellness", use_container_width=True)
        
    if submit_btn:
        log_data = {
            "sleep_duration": sleep_dur,
            "bedtime_hour": bedtime_norm,
            "wake_hour": wake_val,
            "previous_sleep_duration": prev_dur,
            "stress_level": stress,
            "physical_activity": activity,
            "hydration": hydration,
            "screen_time": screen,
            "noise_level": noise,
            "temperature_comfort": temp,
            "light_level": light,
            "bed_comfort": bed
        }
        
        errs = validate_input_ranges(log_data)
        if errs:
            for e in errs:
                st.error(e)
            return
            
        # ML Prediction
        X_df = format_input_features(**log_data)
        if pipeline is not None:
            pred_quality = pipeline.predict(X_df)[0]
            pred_proba = pipeline.predict_proba(X_df)[0]
            class_indices = {cls: idx for idx, cls in enumerate(pipeline.classes_)}
            confidence = round(float(pred_proba[class_indices[pred_quality]]) * 100, 1)
        else:
            pred_quality = "Average"
            confidence = 75.0
            
        # Fetch history for debt & consistency calculations
        history_df = get_all_logs()
        past_durations = [sleep_dur] + (history_df["sleep_duration"].tolist() if not history_df.empty else [])
        past_bedtimes = [bedtime_norm] + (history_df["bedtime_hour"].tolist() if not history_df.empty else [])
        past_waketimes = [wake_val] + (history_df["wake_hour"].tolist() if not history_df.empty else [])
        
        # Calculate composite modules
        s_score = calculate_sleep_score(sleep_dur, stress, screen, noise, temp, light, bed)
        s_debt = calculate_sleep_debt(past_durations)
        c_score = calculate_consistency_score(past_bedtimes, past_waketimes)
        e_score = calculate_environment_score(noise, temp, light, bed)
        h_info = calculate_hydration_impact(hydration, activity)
        r_score = calculate_recovery_score(sleep_dur, prev_dur, stress, activity)
        
        # Save to SQLite DB
        full_log = {
            "log_date": log_date.strftime("%Y-%m-%d"),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **log_data,
            "predicted_quality": pred_quality,
            "sleep_score": s_score,
            "sleep_debt": s_debt,
            "consistency_score": c_score,
            "environment_score": e_score,
            "hydration_status": h_info["status"],
            "recovery_score": r_score,
            "notes": notes
        }
        
        insert_log(full_log)
        
        st.success(f"✅ Sleep check-in for **{log_date}** saved successfully!")
        
        # Display Results Dashboard Card
        st.markdown("---")
        st.subheader("🎯 ML Prediction & Calculated Telemetry")
        
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            badge_html = get_quality_badge_html(pred_quality)
            st.markdown(f"""
                <div class="metric-card" style="text-align: center; padding: 30px;">
                    <div style="font-size: 1rem; color: #94A3B8; font-weight:600;">ML PREDICTED QUALITY</div>
                    <div style="font-size: 2.5rem; font-weight: 800; margin: 10px 0;">{pred_quality.upper()}</div>
                    <div>{badge_html}</div>
                    <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 12px;">Model Confidence: <strong>{confidence}%</strong></div>
                </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("Sleep Score", f"{s_score}/100")
                st.metric("Environment Index", f"{e_score}/100")
            with sc2:
                st.metric("Sleep Debt", f"{s_debt} hrs")
                st.metric("Consistency", f"{c_score}/100")
            with sc3:
                st.metric("Recovery Index", f"{r_score}/100")
                st.metric("Hydration Status", h_info["status"])
                
        # Recommendations
        rec_data = generate_recommendations(full_log)
        st.markdown("---")
        st.subheader("💡 AI Recommendations & Action Plan")
        
        for r in rec_data["recommendations"]:
            st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title">{r['icon']} {r['title']} ({r['category']})</div>
                    <div class="rec-detail">{r['detail']}</div>
                    <div class="rec-action">👉 Recommended Action: {r['action']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with st.expander("📅 Personalized Daily Schedule Plan"):
            for plan_item in rec_data["daily_plan"]:
                st.markdown(f"- {plan_item}")

if __name__ == "__main__":
    from utils.helpers import inject_custom_css
    from database.database import init_db
    init_db()
    inject_custom_css()
    render()
