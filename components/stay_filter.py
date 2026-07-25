from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

BARBADOS_TIMEZONE = ZoneInfo("America/Barbados")


def _set_quick_filter(option: str, days: int) -> None:
    today = datetime.now(BARBADOS_TIMEZONE).date()
    start_date = today if option == "Today" else today + timedelta(days=1)
    end_date = start_date + timedelta(days=days - 1)

    st.session_state.filter_quick_option = option
    st.session_state.filter_arrival_from = start_date
    st.session_state.filter_arrival_to = end_date
    st.session_state.filter_departure_from = start_date
    st.session_state.filter_departure_to = end_date


def _apply_filters() -> None:
    st.session_state.applied_arrival_from = st.session_state.filter_arrival_from
    st.session_state.applied_arrival_to = st.session_state.filter_arrival_to
    st.session_state.applied_departure_from = st.session_state.filter_departure_from
    st.session_state.applied_departure_to = st.session_state.filter_departure_to


def render_stay_filter() -> None:
    st.markdown(
        """
        <div class="stay-filter-heading">
            <div>
                <div class="stay-filter-title">Date Filter</div>
                <div class="stay-filter-subtitle">
                    Select the arrival and departure date ranges to load guests.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    quick_columns = st.columns([1, 1, 1, 1.2, 3.8], gap="small")
    quick_options = (
        ("Today", 1),
        ("Tomorrow", 1),
        ("Next 7 Days", 7),
        ("Next 30 Days", 30),
    )

    for column, (label, days) in zip(quick_columns[:4], quick_options):
        with column:
            active = st.session_state.filter_quick_option == label
            if st.button(
                label,
                key=f"quick_filter_{label}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                _set_quick_filter(label, days)
                _apply_filters()
                st.rerun()

    with quick_columns[4]:
        st.markdown(
            f'<div class="filter-active-label">Active: '
            f'{st.session_state.filter_quick_option}</div>',
            unsafe_allow_html=True,
        )

    with st.form("stay_date_filter_form", border=False):
        arrival_label, arrival_from_col, arrival_to_col = st.columns(
            [0.58, 1.18, 1.18],
            gap="small",
        )
        with arrival_label:
            st.markdown(
                '<div class="date-group-label">Arrival Date</div>',
                unsafe_allow_html=True,
            )
        with arrival_from_col:
            st.date_input("From", key="filter_arrival_from")
        with arrival_to_col:
            st.date_input("To", key="filter_arrival_to")

        departure_label, departure_from_col, departure_to_col = st.columns(
            [0.58, 1.18, 1.18],
            gap="small",
        )
        with departure_label:
            st.markdown(
                '<div class="date-group-label">Departure Date</div>',
                unsafe_allow_html=True,
            )
        with departure_from_col:
            st.date_input("From", key="filter_departure_from")
        with departure_to_col:
            st.date_input("To", key="filter_departure_to")

        # The button is centered only within the combined width of the date fields,
        # not across the full page including the left labels.
        action_label_space, action_fields = st.columns(
            [0.58, 2.36],
            gap="small",
        )
        with action_label_space:
            st.empty()

        with action_fields:
            button_left, button_center, button_right = st.columns(
                [1, 0.62, 1],
                gap="small",
            )
            with button_center:
                submitted = st.form_submit_button(
                    "Load Guests",
                    type="primary",
                    use_container_width=True,
                )

    if submitted:
        if st.session_state.filter_arrival_from > st.session_state.filter_arrival_to:
            st.error("Arrival From cannot be later than Arrival To.")
            return

        if st.session_state.filter_departure_from > st.session_state.filter_departure_to:
            st.error("Departure From cannot be later than Departure To.")
            return

        st.session_state.filter_quick_option = "Custom"
        _apply_filters()
        st.rerun()
