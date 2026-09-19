import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.database import get_dashboard_metrics, seed_sample_history_if_empty
from utils.helpers import render_metric_card, format_hour_to_time_str

def render():
    st.title("📊 Sleep Wellness Dashboard")
    st.caption("Real-time telemetry, composite sleep scores, and AI model predictions.")
    
    seed_sample_history_if_empty()
    metrics = get_dashboard_metrics()
    
    if not metrics or metrics["total_logs"] == 0:
        st.info("No sleep logs recorded yet. Visit the **Daily Check-In** page to log your first sleep record!")
        return
        
    latest = metrics["latest"]
    df = metrics["history_df"].sort_values("log_date", ascending=True)
    
    # 1. Top KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "Latest Quality", 
            latest["predicted_quality"], 
            f"Score: {latest['sleep_score']}/100", 
            badge_type=latest["predicted_quality"]
        )
    with col2:
        render_metric_card(
            "Sleep Duration", 
            f"{latest['sleep_duration']} hrs", 
            f"Bedtime: {format_hour_to_time_str(latest['bedtime_hour'])}"
        )
    with col3:
        render_metric_card(
            "Sleep Debt", 
            f"{latest['sleep_debt']} hrs", 
            "Target: 8.0 hrs baseline"
        )
    with col4:
        render_metric_card(
            "Recovery Index", 
            f"{latest['recovery_score']}/100", 
            f"Consistency: {latest['consistency_score']}/100"
        )
        
    st.markdown("---")
    
    # 2. Charts Section (Two column layout)
    chart_col1, chart_col2 = st.columns([7, 5])
    
    with chart_col1:
        st.subheader("📈 7-Day Sleep & Recovery Trajectory")
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=df["log_date"], y=df["sleep_score"],
            mode="lines+markers", name="Sleep Score",
            line=dict(color="#6366F1", width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=df["log_date"], y=df["recovery_score"],
            mode="lines+markers", name="Recovery Index",
            line=dict(color="#10B981", width=3, dash="dash"),
            marker=dict(size=8)
        ))
        
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            font=dict(color="#E2E8F0"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)", range=[0, 105]),
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with chart_col2:
        st.subheader("🕸️ Latest Environment Comfort Radar")
        categories = ["Noise Control", "Temperature", "Darkness", "Bed Comfort"]
        values = [
            (11 - latest["noise_level"]) * 10,
            latest["temperature_comfort"] * 10,
            (11 - latest["light_level"]) * 10,
            latest["bed_comfort"] * 10
        ]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.3)",
            line=dict(color="#818CF8", width=2)
        ))
        
        fig_radar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
            ),
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    # 3. Secondary Breakdown Section
    st.markdown("---")
    st.subheader("🔍 Breakdown of Latest Log Metrics")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Stress Level", f"{latest['stress_level']}/10", delta="- Lower is better", delta_color="inverse")
    with m_col2:
        st.metric("Screen Time", f"{latest['screen_time']} mins", delta="- Lower is better", delta_color="inverse")
    with m_col3:
        st.metric("Physical Activity", f"{latest['physical_activity']} mins")
    with m_col4:
        st.metric("Hydration Intake", f"{latest['hydration']} L", delta=latest["hydration_status"])

if __name__ == "__main__":
    from utils.helpers import inject_custom_css
    from database.database import init_db
    init_db()
    inject_custom_css()
    render()
