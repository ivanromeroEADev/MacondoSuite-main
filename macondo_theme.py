"""
Colors, fonts and header shared by the three apps.

Call apply() first (it has to be the first Streamlit call), then header().
"""

import os
import sys

import streamlit as st

# Colors
# MUSTARD_DARK is used for hovers and borders.
MUSTARD = "#f0b802"
MUSTARD_DARK = "#c28f00"
BROWN = "#3B2F1E"
BEIGE = "#F5E6C8"
BACKGROUND = "#FFFDF7"

# Typography
# Google Fonts close to the skate wordmark (the real font is proprietary).
TITLE_FONT = "Fredoka"      # titles and the app name (skate style)
BODY_FONT = "Inter"         # body: clean and readable

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family={TITLE_FONT.replace(' ', '+')}:wght@400;500;600;700&family={BODY_FONT.replace(' ', '+')}:wght@400;500;600&display=swap');

:root {{
    --macondo-mustard: {MUSTARD};
    --macondo-mustard-dark: {MUSTARD_DARK};
    --macondo-brown: {BROWN};
    --macondo-beige: {BEIGE};
}}

/* Body typography. Applied to the text containers, not with '*',
   so the icons don't break (they use their own icon font). */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] .stMarkdown,
div[data-baseweb="select"], input, textarea, button {{
    font-family: '{BODY_FONT}', 'Segoe UI', system-ui, sans-serif;
}}

/* Titles and headings with the skate-style font. */
h1, h2, h3, h4, .macondo-title {{
    font-family: '{TITLE_FONT}', '{BODY_FONT}', sans-serif !important;
    letter-spacing: 0.3px;
}}

/* The app name, next to the logo. */
.macondo-title {{
    color: var(--macondo-mustard-dark);
    font-weight: 700;
    font-size: 2.1rem;
    margin: 0;
    line-height: 1.1;
}}

/* Primary buttons (Connect, Generate with AI, Confirm and send). */
div.stButton > button[kind="primary"] {{
    background-color: var(--macondo-mustard);
    border-color: var(--macondo-mustard-dark);
    color: var(--macondo-brown);
    font-weight: 600;
}}
div.stButton > button[kind="primary"]:hover {{
    background-color: var(--macondo-mustard-dark);
    border-color: var(--macondo-mustard-dark);
    color: #FFFDF7;
}}

/* Secondary buttons: same shade but outline only. */
div.stButton > button[kind="secondary"] {{
    border-color: var(--macondo-mustard-dark);
    color: var(--macondo-brown);
}}
div.stButton > button[kind="secondary"]:hover {{
    background-color: var(--macondo-beige);
    border-color: var(--macondo-mustard-dark);
}}

/* Status messages in warm tones, instead of Streamlit's red/green/blue. */
div[data-testid="stAlertContainer"] {{ border-radius: 6px; }}
div[data-testid="stAlertContainer"][class*="success"],
div[data-baseweb="notification"][kind="positive"] {{
    background-color: #EFE6C8; color: var(--macondo-brown);
}}
div[data-testid="stAlertContainer"][class*="warning"] {{
    background-color: #F5DDA0; color: var(--macondo-brown);
}}
div[data-testid="stAlertContainer"][class*="error"] {{
    background-color: #E8C9A0; color: var(--macondo-brown);
}}

/* Yellow spinner. */
div[data-testid="stSpinner"] > div {{ border-top-color: var(--macondo-mustard) !important; }}

/* Tabs (combined suite): the active one in yellow. */
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--macondo-mustard-dark); }}
div[data-baseweb="tab-highlight"] {{ background-color: var(--macondo-mustard) !important; }}

/* The header logo, with rounded corners. */
.macondo-logo img {{ border-radius: 12px; }}
</style>
"""


def apply(page_title, page_icon="🦋"):
    """Page config plus the Macondo CSS. Must be the first Streamlit call."""
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")
    st.markdown(_CSS, unsafe_allow_html=True)


def _logo_path():
    """Path to the logo, whether running from the code or from the .exe (PyInstaller folder)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "macondo_logo.jpg")


def header(title):
    """Draws the header: the butterfly logo on the left and the app name."""
    logo = _logo_path()
    col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
    if os.path.exists(logo):
        col_logo.markdown('<div class="macondo-logo">', unsafe_allow_html=True)
        col_logo.image(logo)
        col_logo.markdown("</div>", unsafe_allow_html=True)
    col_title.markdown(f"<h1 class='macondo-title'>{title}</h1>", unsafe_allow_html=True)
