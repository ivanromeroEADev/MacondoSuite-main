"""
Macondo WorkLogger on its own (no AI, so no Groq key).

Dev mode:  python -m streamlit run worklogger_app.py
"""

import streamlit as st

import macondo_theme
import macondo_login
import worklogger_ui

macondo_theme.apply("Macondo WorkLogger")
macondo_theme.header("Macondo WorkLogger")

# The WorkLogger doesn't use AI: it only needs the JaaS token.
if not macondo_login.login_gate(need_groq=False):
    st.stop()

worklogger_ui.render()
