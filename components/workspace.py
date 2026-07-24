from __future__ import annotations

from typing import Any

import streamlit as st

from components.document_panel import render_document_panel
from components.guest_summary import render_guest_summary
from components.history import render_history
from components.workflow import render_workflow
from services.guest_service import get_guest_by_id


def render_workspace(guests: list[dict[str, Any]]) -> None:
    guest = get_guest_by_id(guests, st.session_state.selected_guest_id)
    render_guest_summary(guest)

    content_col, action_col = st.columns([0.62, 0.38], gap="large")
    with content_col:
        render_document_panel(guest)
    with action_col:
        render_workflow(guest)
        render_history(guest)
