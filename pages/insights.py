import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.database import get_all_logs, seed_sample_history_if_empty

def render():
    st.title("💡 Analytics & Sleep Insights")
    st.caption("Statistical correlations and feature impact analysis on sleep wellness.")
    
    seed_sample_history_if_empty()
    df = get_all_logs()
    
    if df.empty:
        st.info("No sleep logs recorded yet. Visit **Daily Check-In** to log your first sleep record.")
        return
        
    st.subheader("1. Digital Hygiene vs Sleep Quality")
    fig_screen = px.scatter(
        df, x="screen_time", y="sleep_score",
        color="predicted_quality", size="stress_level",
        hover_data=["log_date", "sleep_duration"],
        labels={"screen_time": "Pre-Bed Screen Time (mins)", "sleep_score": "Composite Sleep Score (0-100)"},
        color_discrete_map={"Good": "#10B981", "Average": "#F59E0B", "Poor": "#EF4444"},
        title="Impact of Pre-Bed Screen Time on Sleep Score (Size = Stress Level)"
    )
    fig_screen.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font=dict(color="#E2E8F0"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
    )
    st.plotly_chart(fig_screen, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("2. Stress vs Physical Recovery")
        fig_stress = px.box(
            df, x="stress_level", y="recovery_score",
            color="stress_level",
            labels={"stress_level": "Perceived Stress (1-10)", "recovery_score": "Recovery Score (0-100)"},
            title="Recovery Score Distribution by Daily Stress Level"
        )
        fig_stress.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            font=dict(color="#E2E8F0"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_stress, use_container_width=True)
        
    with col2:
        st.subheader("3. Environmental Factors vs Quality")
        fig_env = px.histogram(
            df, x="predicted_quality", y="environment_score",
            histfunc="avg", color="predicted_quality",
            color_discrete_map={"Good": "#10B981", "Average": "#F59E0B", "Poor": "#EF4444"},
            labels={"environment_score": "Avg Environment Comfort", "predicted_quality": "Predicted Quality"},
            title="Average Environmental Comfort Score by Sleep Quality Category"
        )
        fig_env.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            font=dict(color="#E2E8F0"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)")
        )
        st.plotly_chart(fig_env, use_container_width=True)
        
    st.markdown("---")
    st.subheader("📊 Feature Summary Statistics")
    num_cols = ["sleep_duration", "stress_level", "physical_activity", "hydration", "screen_time", "sleep_score", "recovery_score"]
    stats_df = df[num_cols].describe().T[["mean", "std", "min", "50%", "max"]]
    stats_df.columns = ["Mean", "Std Dev", "Min", "Median", "Max"]
    stats_df = stats_df.round(2)
    st.dataframe(stats_df, use_container_width=True)
    
    # 5. Live What-If Sleep Simulator
    st.markdown("---")
    st.subheader("🧪 Live Interactive 'What-If' Sleep Simulator")
    st.caption("Simulate how altering your habits and bedroom environment impacts your predicted sleep quality and wellness score in real time.")
    
    import os, joblib
    from utils.preprocessing import format_input_features
    from modules.sleep_score import calculate_sleep_score
    
    model_path = os.path.join("model", "sleep_model.pkl")
    pipeline = joblib.load(model_path) if os.path.exists(model_path) else None
    
    sc1, sc2 = st.columns(2)
    with sc1:
        sim_duration = st.slider("Simulated Sleep Duration (hours)", 4.0, 10.0, 8.0, step=0.5)
        sim_stress = st.slider("Simulated Stress Level (1-10)", 1, 10, 3)
        sim_screen = st.slider("Simulated Screen Time (minutes)", 0, 180, 20, step=10)
        sim_activity = st.slider("Simulated Physical Activity (minutes)", 0, 120, 45, step=15)
    with sc2:
        sim_noise = st.slider("Simulated Noise Level (1Quiet - 10Loud)", 1, 10, 2)
        sim_temp = st.slider("Simulated Room Temp Comfort (1-10)", 1, 10, 8)
        sim_light = st.slider("Simulated Light Level (1Dark - 10Bright)", 1, 10, 2)
        sim_bed = st.slider("Simulated Bed Comfort (1-10)", 1, 10, 8)
        
    sim_input = {
        "sleep_duration": sim_duration, "bedtime_hour": 22.5, "wake_hour": 6.5,
        "previous_sleep_duration": sim_duration, "stress_level": sim_stress,
        "physical_activity": sim_activity, "hydration": 2.5, "screen_time": sim_screen,
        "noise_level": sim_noise, "temperature_comfort": sim_temp,
        "light_level": sim_light, "bed_comfort": sim_bed
    }
    
    sim_score = calculate_sleep_score(sim_duration, sim_stress, sim_screen, sim_noise, sim_temp, sim_light, sim_bed)
    
    if pipeline:
        sim_df = format_input_features(**sim_input)
        sim_pred = pipeline.predict(sim_df)[0]
        sim_probas = pipeline.predict_proba(sim_df)[0]
        classes = list(pipeline.classes_)
    else:
        sim_pred, classes, sim_probas = "Good", ["Average", "Good", "Poor"], [0.2, 0.7, 0.1]
        
    st.markdown("#### Simulation Output")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric("Simulated Sleep Quality", sim_pred.upper())
    with mc2:
        st.metric("Simulated Sleep Score", f"{sim_score}/100")
    with mc3:
        top_prob = max(sim_probas) * 100
        st.metric("Prediction Probability", f"{top_prob:.1f}%")
        
    import plotly.graph_objects as go
    fig_prob = go.Figure(go.Bar(
        x=classes, y=[p * 100 for p in sim_probas],
        marker_color=["#F59E0B", "#10B981", "#EF4444"],
        text=[f"{p*100:.1f}%" for p in sim_probas], textposition="auto"
    ))
    fig_prob.update_layout(
        title="Simulated Target Class Probabilities",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font=dict(color="#E2E8F0"), yaxis=dict(range=[0, 105])
    )
    st.plotly_chart(fig_prob, use_container_width=True)

if __name__ == "__main__":
    from utils.helpers import inject_custom_css
    from database.database import init_db
    init_db()
    inject_custom_css()
    render()
