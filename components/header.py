from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


def render_header() -> None:
    barbados_now = datetime.now(ZoneInfo("America/Barbados"))
    date_text = barbados_now.strftime("%A, %d %b, %Y")
    time_text = barbados_now.strftime("%I:%M %p")

    burger_label = "✕" if st.session_state.get("sidebar_open", True) else "☰"
    if st.button(
        burger_label,
        key="toggle_sidebar",
        help="Show or hide navigation",
    ):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

    state_class = "gcp-sidebar-open" if st.session_state.sidebar_open else "gcp-sidebar-closed"

    header_html = (
        f'<span class="{state_class}"></span>'
        '<div class="gcp-header">'
        '<div class="gcp-header-left">'
        '<div class="gcp-brand">GCP</div>'
        '<div class="gcp-divider"></div>'
        '<div class="gcp-product-name">Guest Communication Platform</div>'
        '</div>'
        '<div class="gcp-header-right">'
        '<div class="gcp-date-time">'
        f'<div class="gcp-date">{date_text}</div>'
        f'<div class="gcp-time">{time_text} AST</div>'
        '</div>'
        '<div class="gcp-user">'
        '<div class="gcp-avatar">FD</div>'
        '<div class="gcp-user-info">'
        '<div class="gcp-hotel">SANDY LANE</div>'
        '<div class="gcp-username">FD001</div>'
        '</div></div></div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)
