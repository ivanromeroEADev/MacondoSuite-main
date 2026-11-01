"""
Macondo Suite: Bug Logger and WorkLogger in tabs, sharing one login.

Dev mode:  python -m streamlit run macondo_suite_app.py
"""

import streamlit as st

import macondo_theme
import macondo_login
import bug_logger_ui
import worklogger_ui

macondo_theme.apply("Macondo Suite")
macondo_theme.header("Macondo Suite")

# There's a tab with AI (Bug Logger), so the connection asks for the Groq API Key.
# That same session also works for the WorkLogger.
if not macondo_login.login_gate(need_groq=True):
    st.stop()

tab_bug, tab_work = st.tabs(["🐞 Bug Logger", "⏱️ WorkLogger"])
with tab_bug:
    bug_logger_ui.render()
with tab_work:
    worklogger_ui.render()
