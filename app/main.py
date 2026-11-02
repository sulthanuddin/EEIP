import sys
from pathlib import Path

from app.core.dashboard import render_dashboard

import streamlit as st


# Establish project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# from app.core.dashboard import render_dashboard


# Application configuration
st.set_page_config(
    page_title="EEIP | Electrical Engineering Platform",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Render application
render_dashboard()
