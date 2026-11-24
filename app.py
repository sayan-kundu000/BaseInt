"""Main entrypoint for BaseInt Streamlit application.

Usage:
    streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ui.dashboard import render_dashboard

# Render dashboard on every Streamlit script execution
render_dashboard()
