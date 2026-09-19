import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Modern Glassmorphic Dark UI Theme */
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
            color: #F8FAFC;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Metric Card Container */
        .metric-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.25);
        }
        
        .metric-title {
            color: #94A3B8;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        .metric-value {
            color: #FFFFFF;
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.1;
        }
        .metric-sub {
            color: #CBD5E1;
            font-size: 0.85rem;
            margin-top: 6px;
        }
        
        /* Custom Badges */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .badge-good {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34D399;
            border: 1px solid rgba(52, 211, 153, 0.4);
        }
        .badge-avg {
            background-color: rgba(245, 158, 11, 0.2);
            color: #FBBF24;
            border: 1px solid rgba(251, 191, 36, 0.4);
        }
        .badge-poor {
            background-color: rgba(239, 68, 68, 0.2);
            color: #FCA5A5;
            border: 1px solid rgba(252, 165, 165, 0.4);
        }
        
        /* Recommendation Cards */
        .rec-card {
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid #6366F1;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }
        .rec-title {
            font-weight: 700;
            color: #818CF8;
            font-size: 1rem;
        }
        .rec-detail {
            color: #E2E8F0;
            font-size: 0.9rem;
            margin-top: 4px;
        }
        .rec-action {
            color: #34D399;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 6px;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, subtext="", badge_type=None):
    badge_html = ""
    if badge_type:
        if badge_type.lower() == "good":
            badge_html = '<span class="badge badge-good">Good</span>'
        elif badge_type.lower() == "average":
            badge_html = '<span class="badge badge-avg">Average</span>'
        elif badge_type.lower() == "poor":
            badge_html = '<span class="badge badge-poor">Poor</span>'
            
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{title} {badge_html}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def format_hour_to_time_str(hour_float):
    """
    Converts 22.5 to '10:30 PM' and 0.5 to '12:30 AM'
    """
    try:
        h = float(hour_float) % 24
        hours = int(h)
        minutes = int(round((h - hours) * 60))
        if minutes >= 60:
            hours = (hours + 1) % 24
            minutes = 0
            
        period = "AM" if hours < 12 else "PM"
        disp_hour = hours % 12
        if disp_hour == 0:
            disp_hour = 12
            
        return f"{disp_hour:02d}:{minutes:02d} {period}"
    except Exception:
        return f"{hour_float} hrs"

def get_quality_badge_html(quality_str):
    q = str(quality_str).lower()
    if q == "good":
        return '<span class="badge badge-good">GOOD</span>'
    elif q == "average":
        return '<span class="badge badge-avg">AVERAGE</span>'
    else:
        return '<span class="badge badge-poor">POOR</span>'
