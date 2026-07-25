from __future__ import annotations

import streamlit as st

from components.guest_list import render_guest_list
from components.header import render_header
from components.sidebar import render_sidebar
from components.stay_filter import render_stay_filter
from components.workspace import render_workspace
from services.guest_service import filter_guests_by_stay_dates, load_guests
from utils.state import ensure_selected_guest, initialize_state
from utils.styles import apply_global_styles


st.set_page_config(
    page_title="GCP — Guest Communication Platform",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
guests = load_guests()
initialize_state(guests)

render_header()

# The navigation is rendered in Streamlit's independent sidebar layer.
# This keeps the application workspace white and prevents sidebar styles
# from leaking into the main content area.
with st.sidebar:
    render_sidebar()

active_page = st.session_state.get("active_page", "communications")

if active_page != "communications":
    page_titles = {
        "dashboard": "Dashboard",
        "templates": "Templates",
        "history": "Communication History",
        "administration": "Administration",
        "settings": "Settings",
        "help": "Help",
        "about": "About GCP",
    }

    title = page_titles.get(active_page, "GCP")
    st.markdown(
        f"""
        <div class="empty-workspace-card">
            <div class="empty-workspace-icon">▤</div>
            <div class="empty-workspace-title">{title}</div>
            <div class="empty-workspace-text">
                This module is ready for the next development phase.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
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
        if not filtered_guests:
            st.info(
                "No arrivals or departures were found for the selected date ranges."
            )
        elif st.session_state.selected_guest_id is None:
            st.markdown(
                """
                <div class="empty-workspace-card">
                    <div class="empty-workspace-icon">▤</div>
                    <div class="empty-workspace-title">Please select a reservation</div>
                    <div class="empty-workspace-text">
                        Choose an arrival or departure from the Guest List to view
                        the reservation details and communication workflow.
                    </div>
                </div>
                <div class="empty-workspace-card empty-workspace-secondary">
                    <div class="empty-workspace-section-title">Document & Communication</div>
                    <div class="empty-workspace-placeholder">
                        Please select a reservation to generate a letter, open it in
                        Microsoft Word 365, or send an email.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            render_workspace(filtered_guests)
