from __future__ import annotations

from typing import Any

import streamlit as st


def render_history(guest: dict[str, Any]) -> None:
    st.markdown('<div class="document-card"><div class="panel-title">Communication History</div>', unsafe_allow_html=True)
    events = st.session_state.activity.get(guest["id"], [])
    if not events:
        st.markdown('<div class="muted">No communication activity yet.</div>', unsafe_allow_html=True)
    else:
        for event in events:
            st.markdown(
                f"""
                <div class="history-item">
                  <div class="history-time">{event['time']}</div>
                  <div class="history-message">{event['message']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
