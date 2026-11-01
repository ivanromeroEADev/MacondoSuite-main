"""
Login screen shared by the three apps.

Asks for the JaaS token, plus the Groq key when the app uses AI, and keeps both
encrypted with keyring. login_gate() returns True once connected.
"""

import streamlit as st
from groq import Groq

import core  # shared core: token, Groq key and connection check


def _connect(jaas_token, remember, need_groq, groq_key):
    """Checks the token against JaaS and, if it's valid, saves the session. Returns True/False."""
    if not jaas_token:
        st.error("The JaaS PAT Token is missing.")
        return False

    with st.spinner("Connecting to JaaS..."):
        ok, display_name, username = core.test_connection(jaas_token)

    if not ok:
        st.error("Invalid token. Check that you copied all of it and that it hasn't expired.")
        return False

    if remember:
        core.save_jaas_token(jaas_token)

    # Data the rest of the app uses to talk to JaaS and show who you are.
    st.session_state.jaas_token = jaas_token
    st.session_state.reporter = username
    st.session_state.user_display_name = display_name
    if need_groq:
        st.session_state.groq_client = Groq(api_key=groq_key)
    st.session_state.connected = True
    return True


def login_gate(need_groq):
    """
    Draws the connection screen if there's no session. Returns True once connected.
    'need_groq' is True for the Bug Logger (uses AI) and False for the WorkLogger.
    """
    # If we already connected in this session, we show nothing: we just carry on.
    if st.session_state.get("connected"):
        return True

    st.subheader("Connect")

    saved_token = core.load_jaas_token()

    # Groq API Key (only if the app uses AI)
    groq_key = core.get_groq_key() if need_groq else None
    if need_groq and not groq_key:
        st.info("First time on this computer: paste your Groq API Key once, it's stored encrypted.")
        groq_key_input = st.text_input("Groq API Key", type="password", key="groq_key_input")
        if st.button("Save Groq API Key", key="btn_save_groq"):
            if groq_key_input:
                core.save_groq_key(groq_key_input)
                st.rerun()
            else:
                st.error("Paste a key before saving.")

    # JaaS token
    if saved_token:
        st.success("JaaS token saved on this computer. No need to paste it again.")
        if st.button("Forget token", key="btn_forget"):
            core.delete_jaas_token()
            st.rerun()
        jaas_token = saved_token
        remember = False  # it's already saved, there's nothing to save again
    else:
        jaas_token = st.text_input("JaaS PAT Token", type="password", key="jaas_token_input")
        remember = st.checkbox(
            "Remember on this computer (encrypted, Windows Credential Manager)", value=True
        )

    # The Connect button is disabled if the Groq key is missing in an app that needs it.
    disabled = need_groq and not groq_key
    if st.button("Connect", type="primary", disabled=disabled, key="btn_connect"):
        if _connect(jaas_token, remember, need_groq, groq_key):
            st.rerun()

    return st.session_state.get("connected", False)
