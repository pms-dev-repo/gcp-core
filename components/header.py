from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import streamlit as st

from core.config import get_default_client_code, load_client_config


def _get_timezone_name(config: dict) -> str:
    """
    Return the hotel's configured IANA timezone.

    Supported locations:
    - config["client"]["timezone"]
    - config["timezone"]
    - config["property"]["timezone"]

    Falls back to UTC when no timezone is configured.
    """
    client = config.get("client") or {}
    property_config = config.get("property") or {}

    timezone_name = (
        client.get("timezone")
        or config.get("timezone")
        or property_config.get("timezone")
        or "UTC"
    )

    return str(timezone_name).strip() or "UTC"


def _get_hotel_datetime(config: dict) -> datetime:
    """Return the current date and time in the hotel's configured timezone."""
    timezone_name = _get_timezone_name(config)

    try:
        return datetime.now(ZoneInfo(timezone_name))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return datetime.now(ZoneInfo("UTC"))


def render_header() -> None:
    client_code = str(
        st.session_state.get(
            "active_client_code",
            get_default_client_code(),
        )
    )

    config = load_client_config(client_code)
    client = config.get("client") or {}

    local_now = _get_hotel_datetime(config)

    date_text = local_now.strftime("%A, %d %b, %Y")
    time_text = local_now.strftime("%I:%M %p").lstrip("0")

    hotel_name = str(client.get("name") or "Hotel").upper()

    user = client.get("user") or {}
    user_initials = str(user.get("initials") or "FD")
    user_code = str(user.get("code") or "FD001")

    st.session_state.setdefault("sidebar_open", True)

    if st.button(
        "☰",
        key="toggle_sidebar",
        help="Show or hide navigation",
    ):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

    state_class = (
        "gcp-sidebar-open"
        if st.session_state.sidebar_open
        else "gcp-sidebar-closed"
    )

    header_html = (
        f'<span class="{state_class}"></span>'
        '<div class="gcp-header">'
        '<div class="gcp-header-left">'
        '<div class="gcp-brand"></div>'
        '<div class="gcp-divider"></div>'
        '<div class="gcp-product-name"></div>'
        '</div>'
        '<div class="gcp-header-right">'
        '<div class="gcp-date-time">'
        f'<div class="gcp-date">{date_text}</div>'
        f'<div class="gcp-time">{time_text}</div>'
        '</div>'
        f'<div class="gcp-active-hotel-chip">{hotel_name}</div>'
        '<div class="gcp-user">'
        f'<div class="gcp-avatar">{user_initials}</div>'
        '<div class="gcp-user-info">'
        f'<div class="gcp-hotel">{hotel_name}</div>'
        f'<div class="gcp-username">{user_code}</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )
