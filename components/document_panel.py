from __future__ import annotations

from typing import Any

import streamlit as st


def render_document_panel(guest: dict[str, Any]) -> None:
    generated = st.session_state.document_status.get(guest["id"], False)
    st.markdown(
        f"""
        <div class="document-card">
          <div class="panel-title">Document</div>
          <div class="document-row"><span>Template</span><span>{guest['template']['name']}</span></div>
          <div class="document-row"><span>Language</span><span>{guest['template']['language']}</span></div>
          <div class="document-row"><span>Output</span><span>Microsoft Word (.docx)</span></div>
          <div class="document-row"><span>Email</span><span>{guest.get('email') or 'Missing email'}</span></div>
          <div class="document-row"><span>Confirmation</span><span>{guest['confirmation_number']}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if generated:
        st.markdown(
            f"""
            <div class="preview-box">
              <div class="paper">
                <strong>{guest['template']['name']}</strong><br><br>
                Dear {guest['first_name']} {guest['last_name']},<br><br>
                Welcome to Sandy Lane. We are delighted to welcome you on
                {guest['stay']['arrival_date']}. Your room is {guest['room']} and
                your expected arrival time is {guest['transport']['eta']}.<br><br>
                Warm regards,<br>Guest Relations
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="preview-box" style="display:flex;align-items:center;justify-content:center">
              <div style="text-align:center;color:#6b7280">
                <div style="font-size:32px;margin-bottom:8px">📄</div>
                No document generated yet.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
