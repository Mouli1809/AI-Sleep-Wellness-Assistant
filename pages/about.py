import os
import json
import pandas as pd
import streamlit as st

META_PATH = os.path.join("model", "model_metadata.json")

def render():
    st.title("ℹ️ About AI Sleep Wellness Assistant")
    st.caption("College-level Demonstration & Technical Architecture Documentation.")
    
    st.markdown("""
    ### 🎯 Overview
    The **AI-Powered Sleep Wellness Assistant** is a production-quality, locally runnable web application built to analyze sleep patterns, evaluate physical and environmental sleep drivers, and predict sleep quality categories using machine learning.
    
    ---
    ### 🛠️ Technology Stack
    - **UI & Multi-page Framework:** Streamlit (Python)
    - **Machine Learning Engine:** Scikit-learn (`StandardScaler` + `RandomForestClassifier`)
    - **Data Processing & Analytics:** Pandas & NumPy
    - **Data Visualization:** Plotly Express & Plotly Graph Objects
    - **Storage Engine:** SQLite (`sleep_wellness.db`)
    - **Model Serialization:** Joblib
    """)
    
    st.markdown("---")
    st.subheader("🤖 Machine Learning Model Metrics & Feature Importances")
    
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            meta = json.load(f)
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Test Accuracy", f"{meta.get('accuracy', 0)*100:.1f}%")
        with col2:
            st.metric("Dataset Size", f"{meta.get('dataset_size', 0)} rows")
        with col3:
            st.metric("Train Split", f"{meta.get('train_size', 0)} rows")
        with col4:
            st.metric("Test Split", f"{meta.get('test_size', 0)} rows")
            
        st.markdown(f"**Trained At:** `{meta.get('trained_at', 'N/A')}`")
        st.markdown(f"**Target Classes:** `{', '.join(meta.get('classes', []))}`")
        
        st.write("#### Feature Importances")
        imp_df = {"Feature": list(meta.get("feature_importances", {}).keys()),
                  "Importance Weight": list(meta.get("feature_importances", {}).values())}
        st.dataframe(imp_df, use_container_width=True)
    else:
        st.info("Model metadata not found. Train the model by running `python model/train_model.py`.")
        
    # Benchmarking Comparison Section
    bench_path = os.path.join("model", "model_benchmarks.json")
    if os.path.exists(bench_path):
        st.markdown("---")
        st.subheader("📊 Multi-Algorithm Benchmark Comparison")
        with open(bench_path, "r") as f:
            bench_data = json.load(f)
            
        bench_df = pd.DataFrame(bench_data).T.reset_index()
        bench_df.columns = ["Algorithm", "Accuracy (%)", "F1-Score (%)", "Precision (%)", "Recall (%)"]
        
        st.dataframe(bench_df, use_container_width=True)
        
        import plotly.express as px
        fig_bench = px.bar(
            bench_df, x="Algorithm", y="Accuracy (%)",
            color="Algorithm", text="Accuracy (%)",
            title="Accuracy Comparison Across ML Classification Algorithms",
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B", "#EF4444"]
        )
        fig_bench.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.5)",
            font=dict(color="#E2E8F0"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)", range=[0, 100])
        )
        st.plotly_chart(fig_bench, use_container_width=True)
        
    st.markdown("---")
    st.subheader("🏗️ System Architecture & Workflow")
    st.markdown("""
    ```
    ┌───────────────────────────┐      ┌───────────────────────────┐
    │  Synthetic Sleep Dataset  │ ───► │  sklearn Pipeline (RF)    │
    │  (1,500 sample records)   │      │  StandardScaler + RF      │
    └───────────────────────────┘      └─────────────┬─────────────┘
                                                     │
                                                     ▼
    ┌───────────────────────────┐      ┌───────────────────────────┐
    │  Streamlit Multi-Page UI  │ ◄─── │   model/sleep_model.pkl   │
    │  (app.py Router)          │      │   + model_metadata.json   │
    └─────────────┬─────────────┘      └───────────────────────────┘
                  │
                  ▼
    ┌───────────────────────────┐      ┌───────────────────────────┐
    │  Wellness Scoring Engine  │ ───► │  SQLite Local Storage     │
    │  (6 Composite Metrics)    │      │  (database/sleep_w.db)    │
    └───────────────────────────┘      └───────────────────────────┘
    ```
    """)
    
    st.markdown("---")

if __name__ == "__main__":
    from utils.helpers import inject_custom_css
    from database.database import init_db
    init_db()
    inject_custom_css()
    render()
