from __future__ import annotations

from typing import Any

import streamlit as st

from components.status import status_badge
from utils.state import get_status


def render_guest_summary(guest: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="summary-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div class="summary-title">👤 {guest['full_name']}</div>
              <div class="summary-subtitle">Room {guest['room']} · ⭐ {guest['vip_level']}</div>
            </div>
            <div>{status_badge(get_status(guest))}</div>
          </div>
          <div class="mini-grid">
            <div class="mini-card"><div class="mini-label">Arrival</div><div class="mini-value">{guest['stay']['arrival_date']}</div></div>
            <div class="mini-card"><div class="mini-label">Departure</div><div class="mini-value">{guest['stay']['departure_date']}</div></div>
            <div class="mini-card"><div class="mini-label">Nights</div><div class="mini-value">{guest['stay']['nights']}</div></div>
            <div class="mini-card"><div class="mini-label">Guests</div><div class="mini-value">{guest['stay']['adults']} Adults · {guest['stay']['children']} Child</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
