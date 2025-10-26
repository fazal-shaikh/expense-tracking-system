import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab

# --- Global CSS for background and general styling ---
st.markdown("""
    <style>
    /* Full app background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
        color: #102a43;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Card style */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }

    /* Header style */
    .css-18e3th9 {padding-top: 2rem;}  /* adjust top padding */

    /* Table styling */
    .stDataFrame table {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- App title ---
st.title("💼 Expense Tracking System")

# --- Tabs ---
tab1, tab2 = st.tabs(["Add/Update", "Analytics"])

with tab1:
    add_update_tab()

with tab2:
    analytics_tab()
