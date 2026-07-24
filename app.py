from __future__ import annotations

import streamlit as st

from components.guest_list import render_guest_list
from components.header import render_header
from components.stay_filter import render_stay_filter
from components.workspace import render_workspace
from services.guest_service import filter_guests_by_stay_dates, load_guests
from utils.state import ensure_selected_guest, initialize_state
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
render_stay_filter()

filtered_guests = filter_guests_by_stay_dates(
    guests=guests,
    arrival_from=st.session_state.applied_arrival_from,
    arrival_to=st.session_state.applied_arrival_to,
    departure_from=st.session_state.applied_departure_from,
    departure_to=st.session_state.applied_departure_to,
)
ensure_selected_guest(filtered_guests)

left, right = st.columns([0.23, 0.77], gap="large")
with left:
    render_guest_list(filtered_guests)
with right:
    if filtered_guests:
        render_workspace(filtered_guests)
    else:
        st.info(
            "No arrivals or departures were found for the selected date ranges."
        )
