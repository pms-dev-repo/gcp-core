from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer


def _arrival_preview(guest: dict[str, Any]) -> str:
    return f"""
        <strong>{guest['template']['name']}</strong><br><br>
        Dear {guest.get('full_name', '')},<br><br>
        Welcome to Sandy Lane. We are delighted to welcome you on
        {guest.get('stay', {}).get('arrival_date', 'To be confirmed')}.
        Your room is {guest.get('room') or 'To be assigned'} and your expected
        arrival time is {guest.get('transport', {}).get('eta', 'To be confirmed')}.<br><br>
        Our Guest Relations team remains available should you require any assistance.<br><br>
        Warm regards,<br>
        Guest Relations<br>
        Sandy Lane
    """


def _departure_preview(guest: dict[str, Any]) -> str:
    salutation = guest.get("salutation") or ""
    return f"""
        {guest.get('letter_date', '')}<br><br>
        {salutation} {guest.get('full_name', '')}<br>
        In Residence<br>
        Room: {guest.get('room') or 'To be assigned'}<br><br>
        Dear {salutation} {guest.get('last_name', '')},<br><br>
        We hope that you have enjoyed your stay with us and have had the opportunity
        to experience all of our facilities and services.<br><br>
        Your comments are vital in helping us to maintain and improve our resort and
        the services we provide. An invitation to complete our online guest comment
        survey will be emailed to you directly.<br><br>
        Please note that the checkout time from your room is at 12:00pm unless otherwise
        confirmed.<br><br>
        Yours sincerely,<br><br>
        Duty Manager
    """


def _render_pdf_preview(pdf_path: Path, guest_id: str) -> None:
    try:
        pdf_bytes = pdf_path.read_bytes()
    except OSError as exc:
        st.error(f"Could not load the PDF preview: {exc}")
        return

    st.markdown(
        """
        <div style="
            border:1px solid #d7dce5;
            border-radius:12px;
            background:#ffffff;
            padding:14px 16px;
            margin-top:18px;
            margin-bottom:10px;
        ">
            <div style="
                font-weight:600;
                font-size:16px;
                margin-bottom:4px;
            ">
                Final PDF Preview
            </div>
            <div style="
                color:#6b7280;
                font-size:13px;
            ">
                Review the generated document before sending it to the guest.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        pdf_viewer(
            input=pdf_bytes,
            width="100%",
            height=760,
            key=f"pdf_viewer_{guest_id}",
        )
    except Exception as exc:
        st.error(f"Could not display the PDF preview: {exc}")
        st.info(
            "The PDF was generated successfully. "
            "Use the Download Final PDF button to review it."
        )

    st.caption(
        "Final PDF generated from the selected Word document."
    )


def render_document_panel(guest: dict[str, Any]) -> None:
    guest_id = guest["id"]

    generated_path_value = st.session_state.generated_documents.get(guest_id)
    generated_path = (
        Path(generated_path_value)
        if generated_path_value
        else None
    )
    generated = bool(generated_path and generated_path.exists())

    pdf_path_value = st.session_state.get(
        "generated_pdfs",
        {},
    ).get(guest_id)
    pdf_path = Path(pdf_path_value) if pdf_path_value else None
    pdf_ready = bool(pdf_path and pdf_path.exists())

    st.markdown(
        f"""
        <div class="document-card">
          <div class="panel-title">Document</div>
          <div class="document-row"><span>Template</span><span>{guest['template']['name']}</span></div>
          <div class="document-row"><span>Language</span><span>{guest['template']['language']}</span></div>
          <div class="document-row"><span>Output</span><span>Microsoft Word (.docx)</span></div>
          <div class="document-row"><span>Email</span><span>{guest.get('email') or 'Missing email'}</span></div>
          <div class="document-row"><span>Confirmation</span><span>{guest['confirmation_number']}</span></div>
          <div class="document-row"><span>File</span><span>{generated_path.name if generated_path else 'Not generated'}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pdf_ready and pdf_path:
        _render_pdf_preview(pdf_path, guest_id)
        return

    if generated:
        movement = str(guest.get("movement", "")).lower()
        preview_html = (
            _departure_preview(guest)
            if movement == "departures"
            else _arrival_preview(guest)
        )
        st.markdown(
            f"""
            <div class="preview-box">
              <div class="paper">{preview_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "Demo preview. The Download DOCX button uses the real Word "
            "document generated from the selected template."
        )
    else:
        st.markdown(
            """
            <div class="preview-box" style="
                display:flex;
                align-items:center;
                justify-content:center;
            ">
              <div style="text-align:center;color:#6b7280">
                <div style="font-size:32px;margin-bottom:8px">📄</div>
                No document generated yet.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
