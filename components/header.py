from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from core.config import get_default_client_code, load_client_config


def render_header() -> None:
    client_code = str(
        st.session_state.get(
            "active_client_code",
            get_default_client_code(),
        )
    )
    config = load_client_config(client_code)

    client = config.get("client", {})
    branding = client.get("branding", {})
    timezone_name = client.get("timezone", "America/Barbados")

    try:
        local_now = datetime.now(ZoneInfo(timezone_name))
    except Exception:
        local_now = datetime.now(ZoneInfo("UTC"))

    date_text = local_now.strftime("%A, %d %b, %Y")
    time_text = local_now.strftime("%I:%M %p")

    hotel_name = str(client.get("name", "Hotel")).upper()
    user = client.get("user", {})
    user_initials = str(user.get("initials", "FD"))
    user_code = str(user.get("code", "FD001"))

    st.session_state.setdefault("sidebar_open", True)

    burger_label = "☰"
    if st.button(
        burger_label,
        key="toggle_sidebar",
        help="Show or hide navigation",
    ):
        st.session_state.sidebar_open = (
            not st.session_state.sidebar_open
        )
        st.rerun()

    state_class = (
        "gcp-sidebar-open"
        if st.session_state.sidebar_open
        else "gcp-sidebar-closed"
    )

    header_html = (
        f'<span class="{state_class}"></span>'
        '<div class="gcp-header"><div class="gcp-header-left">'
        '<div class="gcp-brand"></div>'
        '<div class="gcp-divider"></div>'
        '<div class="gcp-product-name"></div></div>'
        '<div class="gcp-header-right"><div class="gcp-date-time">'
        f'<div class="gcp-date">{date_text}</div>'
        f'<div class="gcp-time">{time_text}</div></div>'
        f'<div class="gcp-active-hotel-chip">{hotel_name}</div>'
        '<div class="gcp-user">'
        f'<div class="gcp-avatar">{user_initials}</div>'
        '<div class="gcp-user-info">'
        f'<div class="gcp-hotel">{hotel_name}</div>'
        f'<div class="gcp-username">{user_code}</div>'
        '</div></div></div></div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )
