"""
Macondo Logger on its own.

Dev mode:  python -m streamlit run macondo_app.py
"""

import streamlit as st

import macondo_theme
import macondo_login
import bug_logger_ui

macondo_theme.apply("Macondo Logger")
macondo_theme.header("Macondo Logger")

# The Bug Logger uses AI, so the connection also asks for the Groq API Key.
if not macondo_login.login_gate(need_groq=True):
    st.stop()

bug_logger_ui.render()
