import os
import json
import streamlit as st

from utils.helpers import inject_custom_css
from database.database import init_db, seed_sample_history_if_empty

# 1. Initialize DB & sample records
init_db()
seed_sample_history_if_empty()

# 2. Define Streamlit native pages
pg_dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True)
pg_checkin = st.Page("pages/daily_checkin.py", title="Daily Check-In", icon="📝")
pg_history = st.Page("pages/history.py", title="Sleep History", icon="📜")
pg_insights = st.Page("pages/insights.py", title="Analytics & Insights", icon="💡")
pg_about = st.Page("pages/about.py", title="About & Architecture", icon="ℹ️")

# 3. Setup Navigation Menu
pg = st.navigation(
    {
        "Navigation": [pg_dashboard, pg_checkin, pg_history, pg_insights, pg_about]
    }
)

# 4. Global Sidebar Branding & Status Badges
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌙 Sleep Wellness AI")
st.sidebar.caption("Personalized Sleep Telemetry & AI Assistant")

meta_path = os.path.join("model", "model_metadata.json")
if os.path.exists(meta_path):
    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
        acc = meta.get("accuracy", 0.0) * 100
        model_name = meta.get("model_name", "ML Model")
        st.sidebar.success(f"🤖 {model_name} ({acc:.1f}% test Acc)")
    except Exception:
        st.sidebar.info("🤖 RF Model Active")
else:
    st.sidebar.warning("⚠️ Model Pending Training")

st.sidebar.info("💾 SQLite Storage: Active")
st.sidebar.caption("Educational prototype • Synthetic dataset")

# 5. Inject CSS & Execute Selected Page
inject_custom_css()
pg.run()
