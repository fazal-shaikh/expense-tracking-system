import streamlit as st
import requests
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Expense Tracking System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Global CSS Styling (Modern FinTech Glassmorphism)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Full App Background */
    .stApp {
        background: #0F172A;
        color: #F8FAFC;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .hero-title {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 800;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 14px;
        margin: 0;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-size: 12px;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
    }

    .status-offline {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        font-size: 12px;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Card Styling */
    .custom-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Metric Box */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }
    
    .metric-title {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #F8FAFC;
    }

    /* Primary Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        color: white;
        font-weight: 700;
        font-size: 15px;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        width: 100%;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
    }

    /* Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E293B;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Server Connection Check
# ---------------------------------------------------------
API_URL = "http://localhost:8000"
is_connected = False
try:
    res = requests.get(f"{API_URL}/docs", timeout=1.5)
    if res.status_code == 200:
        is_connected = True
except Exception:
    is_connected = False

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.markdown("## 💼 Expense Tracker")
st.sidebar.markdown("### Control Panel")

if is_connected:
    st.sidebar.markdown('<span class="status-badge">🟢 API Server Connected</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="status-offline">🔴 API Server Offline</span>', unsafe_allow_html=True)
    st.sidebar.caption("Run `python -m uvicorn backend.server:app --reload` to launch the API server.")

st.sidebar.markdown("---")
st.sidebar.info("""
**System Overview:**
- Backend: FastAPI + SQLite / MySQL
- Frontend: Streamlit + Plotly Analytics
- Version: v2.0 Glassmorphic Edition
""")

# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
status_html = '<span class="status-badge">🟢 Online</span>' if is_connected else '<span class="status-offline">🔴 Backend Disconnected</span>'

st.markdown(f"""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="hero-title">💼 Expense Tracking System</h1>
            <p class="hero-subtitle">Log daily transactions, manage spending categories, and analyze financial breakdown</p>
        </div>
        <div>{status_html}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# App Tabs
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📝 Add / Manage Expenses", "📊 Analytics & Insights"])

with tab1:
    add_update_tab()

with tab2:
    analytics_tab()
