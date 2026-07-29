from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import streamlit as st

from core.config import load_client_config


def render_header() -> None:
    config = load_client_config()
    client = config.get("client", {})
    branding = client.get("branding", {})

    timezone_name = str(
        client.get("timezone")
        or config.get("timezone")
        or "UTC"
    )

    try:
        local_now = datetime.now(ZoneInfo(timezone_name))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        local_now = datetime.now(ZoneInfo("UTC"))

    date_text = local_now.strftime("%A, %d %b, %Y")
    time_text = local_now.strftime("%I:%M %p").lstrip("0")
    timezone_abbr = local_now.tzname() or "UTC"

    product_name = branding.get("product_name", "GCP")
    product_subtitle = branding.get(
        "product_subtitle",
        "Guest Communication Platform",
    )
    hotel_name = str(client.get("name", "Hotel")).upper()

    st.session_state.setdefault("sidebar_open", True)

    burger_label = (
        "✕"
        if st.session_state.get("sidebar_open", True)
        else "☰"
    )

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
        '<div class="gcp-header">'
        '<div class="gcp-header-left">'
        f'<div class="gcp-brand">{product_name}</div>'
        '<div class="gcp-divider"></div>'
        f'<div class="gcp-product-name">{product_subtitle}</div>'
        '</div>'
        '<div class="gcp-header-right">'
        '<div class="gcp-date-time">'
        f'<div class="gcp-date">{date_text}</div>'
        f'<div class="gcp-time">'
        f'{time_text}'
        f'<span class="gcp-tz">{timezone_abbr}</span>'
        '</div>'
        '</div>'
        '<div class="gcp-user">'
        '<div class="gcp-avatar">FD</div>'
        '<div class="gcp-user-info">'
        f'<div class="gcp-hotel">{hotel_name}</div>'
        '<div class="gcp-username">FD001</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )
