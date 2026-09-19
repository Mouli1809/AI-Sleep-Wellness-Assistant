# 🌙 AI-Powered Sleep Wellness Assistant

A complete, production-quality, locally runnable AI-powered Sleep Wellness Assistant built with Python, Streamlit, Scikit-learn (Random Forest Classifier), SQLite, Plotly, and Pandas — structured as a college-level demonstration project.

---

## 🌟 Key Features

1. **Synthetic Sleep Dataset (1,500 Rows)**: Realistic multi-factor sleep telemetry dataset spanning duration, stress, pre-bed screen time, hydration, activity, and environmental comfort metrics (noise, light, temperature, bed comfort).
2. **Machine Learning Pipeline**: Scikit-learn `Pipeline` (`StandardScaler` + `RandomForestClassifier`) trained to predict Sleep Quality (`Poor`, `Average`, `Good`) with detailed metadata export (`model/model_metadata.json`).
3. **SQLite Database Layer**: Thread-safe database manager (`database/sleep_wellness.db`) tracking daily check-ins, calculated metrics, and notes with seed data support.
4. **6 Wellness Scoring Engines**:
   - **Composite Sleep Score** (0–100)
   - **Accumulated Sleep Debt** (vs 8.0h target)
   - **Bedtime/Wake Consistency Index** (0–100)
   - **Environmental Comfort Index** (0–100)
   - **Hydration Impact Analysis**
   - **Physical & Nervous Recovery Readiness Score** (0–100)
5. **Interactive Streamlit Web Dashboard**:
   - **Dashboard**: High-level KPIs, 7-day trajectory plots, and radar charts.
   - **Daily Check-In**: Input sliders, instant ML quality prediction, score breakdown, and personalized daily action plan generator.
   - **Sleep History**: Tabular view, filtering, log inspector, and delete options.
   - **Analytics & Insights**: Feature correlations, stress vs. recovery box plots, and environmental impact breakdown.
   - **About & Architecture**: Technical documentation, feature importances, system diagram, and academic disclaimer.

---

## 📁 Directory Structure

```
.
├── data/
│   ├── generate_dataset.py       # Script to generate synthetic sleep data
│   └── sleep_dataset.csv         # 1,500-row synthetic sleep dataset
├── model/
│   ├── train_model.py            # Model training & serialization script
│   ├── sleep_model.pkl           # Trained Random Forest pipeline
│   └── model_metadata.json       # Accuracy, feature importances, and metadata
├── database/
│   ├── database.py               # SQLite CRUD helper
│   └── sleep_wellness.db         # SQLite database file
├── modules/
│   ├── sleep_score.py            # Composite 0-100 sleep score calculator
│   ├── sleep_debt.py             # Sleep debt aggregator
│   ├── consistency.py            # Bedtime/wake-time variance score
│   ├── environment.py            # Bedroom comfort score
│   ├── hydration.py             # Hydration sufficiency evaluator
│   ├── recovery.py              # Physical recovery readiness score
│   └── recommendations.py       # Rule-based recommendations & daily plan engine
├── utils/
│   ├── preprocessing.py          # Input formatting & validation
│   └── helpers.py                # CSS injection, metric cards & badges
├── pages/
│   ├── dashboard.py              # Dashboard view module
│   ├── daily_checkin.py          # Daily logging & prediction module
│   ├── history.py                # Table history & detail view module
│   ├── insights.py               # Plotly analytics & correlations
│   └── about.py                  # Project architecture & metadata view
├── app.py                        # Streamlit main entry point & router
├── requirements.txt              # PyPI dependencies
├── README.md                     # Technical documentation
├── app.js, index.html, styles.css # Preserved previous web demo files
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Dataset (Optional - already created)
```bash
python data/generate_dataset.py
```

### 4. Train the ML Model (Optional - pre-trained model included)
```bash
python model/train_model.py
```

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```

The web application will open automatically in your browser at `http://localhost:8501`.

---

## 🎓 College Project Verification Steps

1. **Dataset Verification**: Check `data/sleep_dataset.csv` (1,500 rows, 13 columns).
2. **Model Training Verification**: Run `python model/train_model.py` and inspect accuracy output (≥ 75%) and `model/model_metadata.json`.
3. **App Verification**: Launch `streamlit run app.py` and test:
   - Dashboard KPI rendering
   - Daily Check-In submission & ML prediction
   - History table view & record inspection
   - Insights correlation charts
   - About page architecture overview
