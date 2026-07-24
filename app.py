from __future__ import annotations

import streamlit as st

from components.header import render_header
from components.guest_list import render_guest_list
from components.workspace import render_workspace
from services.guest_service import load_guests
from utils.state import initialize_state
from utils.styles import apply_global_styles

st.set_page_config(
    page_title="GCP — Guest Communication Platform",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_styles()
guests = load_guests()
initialize_state(guests)
render_header()

left, right = st.columns([0.23, 0.77], gap="large")
with left:
    render_guest_list(guests)
with right:
    render_workspace(guests)
