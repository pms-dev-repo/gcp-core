from __future__ import annotations

from typing import Any

import streamlit as st

from services.document_service import build_docx
from services.email_service import send_guest_email
from services.word_service import open_in_word_365
from utils.state import add_activity


def render_workflow(guest: dict[str, Any]) -> None:
    guest_id = guest["id"]
    generated = st.session_state.document_status.get(guest_id, False)
    reviewed = st.session_state.word_opened.get(guest_id, False)
    sent = st.session_state.email_sent.get(guest_id, False)

    st.markdown('<div class="document-card"><div class="panel-title">Workflow</div>', unsafe_allow_html=True)

    if st.button("✨ Generate Document", type="primary"):
        st.session_state.document_status[guest_id] = True
        add_activity(guest_id, "Word document generated")
        st.toast("Document generated successfully.", icon="✅")
        st.rerun()

    docx_bytes = build_docx(guest) if generated else b""
    st.download_button(
        "⬇ Download DOCX",
        data=docx_bytes,
        file_name=f"{guest['template']['code']}_{guest['confirmation_number']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        disabled=not generated,
    )

    if st.button("🟦 Open in Word 365", disabled=not generated):
        open_in_word_365(guest)
        st.session_state.word_opened[guest_id] = True
        add_activity(guest_id, "Document opened in Word 365")
        st.toast("Demo: Word 365 launch requested.", icon="🟦")
        st.rerun()

    if st.button(
        "📧 Send Email",
        disabled=not (generated and reviewed and guest.get("email")),
    ):
        if send_guest_email(guest):
            st.session_state.email_sent[guest_id] = True
            add_activity(guest_id, f"Email sent to {guest['email']}")
            st.toast("Email sent successfully.", icon="📧")
            st.rerun()

    st.markdown("---")
    readiness = [
        ("Guest selected", True),
        ("Email available", bool(guest.get("email"))),
        ("Document generated", generated),
        ("Reviewed in Word", reviewed),
        ("Email sent", sent),
    ]
    for label, done in readiness:
        st.markdown(f"{'✅' if done else '○'} {label}")
    st.markdown("</div>", unsafe_allow_html=True)
