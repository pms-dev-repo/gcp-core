from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from services.document_service import generate_guest_document, read_generated_document
from services.email_service import send_guest_email
from services.word_service import open_in_word_365
from utils.state import add_activity


DOCX_MIME = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def _show_progress(
    steps: list[tuple[str, int, float]],
    action: Callable[[], Any] | None = None,
) -> Any:
    """
    Muestra una experiencia visual tipo Microsoft 365.

    Cada paso contiene:
    - mensaje
    - porcentaje de progreso
    - segundos de espera

    La acción real se ejecuta antes del último paso.
    """
    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    result: Any = None

    for index, (message, progress_value, delay_seconds) in enumerate(steps):
        status_placeholder.info(message)
        progress_bar.progress(progress_value)

        if action is not None and index == len(steps) - 2:
            result = action()

        time.sleep(delay_seconds)

    return result, status_placeholder, progress_bar


def _finish_progress(
    status_placeholder,
    progress_bar,
    success_message: str,
    success_icon: str = "✅",
) -> None:
    progress_bar.progress(100)
    status_placeholder.success(success_message, icon=success_icon)
    time.sleep(0.7)
    progress_bar.empty()
    status_placeholder.empty()




def _open_word_365_experience(
    guest: dict[str, Any],
    generated_path: Path,
) -> str:
    """
    Simula una experiencia de apertura en Microsoft Word 365 usando
    únicamente componentes nativos de Streamlit.
    """
    launcher = st.empty()

    stages = [
        {
            "title": "Preparing your document",
            "progress": 18,
            "active": "Connecting to Microsoft 365...",
            "completed": [],
            "delay": 0.55,
        },
        {
            "title": "Synchronizing document",
            "progress": 42,
            "active": "Retrieving document from OneDrive...",
            "completed": [
                "Connected to Microsoft 365",
            ],
            "delay": 0.55,
        },
        {
            "title": "Authenticating",
            "progress": 68,
            "active": "Validating Word Online session...",
            "completed": [
                "Connected to Microsoft 365",
                "Document synchronized",
            ],
            "delay": 0.55,
        },
        {
            "title": "Loading Word editor",
            "progress": 86,
            "active": "Loading Microsoft Word tools...",
            "completed": [
                "Connected to Microsoft 365",
                "Document synchronized",
                "Session authenticated",
            ],
            "delay": 0.50,
        },
        {
            "title": "Opening document",
            "progress": 97,
            "active": "Launching Microsoft Word...",
            "completed": [
                "Connected to Microsoft 365",
                "Document synchronized",
                "Session authenticated",
                "Word editor loaded",
            ],
            "delay": 0.40,
        },
    ]

    for stage in stages:
        with launcher.container(border=True):
            header_col, title_col = st.columns([1, 7])

            with header_col:
                st.markdown("## 🟦")

            with title_col:
                st.markdown("**Microsoft 365**")
                st.caption("Microsoft Word")

            st.markdown(f"### {stage['title']}")
            st.progress(stage["progress"], text=f"{stage['progress']}%")

            for completed_step in stage["completed"]:
                st.markdown(f"✅ {completed_step}")

            st.info(stage["active"], icon="🔄")

        time.sleep(stage["delay"])

    web_url = open_in_word_365(generated_path)

    with launcher.container(border=True):
        header_col, title_col = st.columns([1, 7])

        with header_col:
            st.markdown("## 🟦")

        with title_col:
            st.markdown("**Microsoft Word**")
            st.caption("Word for the web")

        st.success("Document opened successfully.", icon="✅")
        st.progress(100, text="100%")

        confirmation_number = guest.get(
            "confirmation_number",
            "Guest document",
        )
        st.markdown(f"**Document:** `{confirmation_number}`")
        st.caption("The editing session is ready.")

    time.sleep(0.9)
    launcher.empty()

    return web_url

def render_workflow(guest: dict[str, Any]) -> None:
    guest_id = guest["id"]

    generated_path_value = st.session_state.generated_documents.get(guest_id)
    generated_path = Path(generated_path_value) if generated_path_value else None
    generated = bool(generated_path and generated_path.exists())

    reviewed = st.session_state.word_opened.get(guest_id, False)
    sent = st.session_state.email_sent.get(guest_id, False)

    st.markdown(
        '<div class="document-card"><div class="panel-title">Workflow</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Generate Document",
        type="primary",
        key=f"generate_{guest_id}",
        use_container_width=False,
    ):
        try:
            steps = [
                ("Preparing Word template...", 15, 0.35),
                ("Loading guest information...", 35, 0.40),
                ("Replacing document placeholders...", 60, 0.45),
                ("Creating Microsoft Word document...", 88, 0.35),
                ("Finalizing document...", 96, 0.25),
            ]

            output_path, status_placeholder, progress_bar = _show_progress(
                steps,
                action=lambda: generate_guest_document(guest),
            )

            st.session_state.generated_documents[guest_id] = str(output_path)
            st.session_state.document_status[guest_id] = True
            st.session_state.word_opened[guest_id] = False
            st.session_state.email_sent[guest_id] = False

            add_activity(
                guest_id,
                f"Word document generated: {output_path.name}",
            )

            _finish_progress(
                status_placeholder,
                progress_bar,
                "Document generated successfully.",
            )

            st.toast("Document ready.", icon="✅")
            st.rerun()

        except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
            st.error(f"Could not generate the document: {exc}")

    if generated and generated_path:
        try:
            docx_bytes = read_generated_document(generated_path)
        except OSError as exc:
            docx_bytes = b""
            st.error(f"Could not read the generated document: {exc}")
    else:
        docx_bytes = b""

    st.download_button(
        "⬇ Download DOCX",
        data=docx_bytes,
        file_name=generated_path.name if generated_path else "guest_letter.docx",
        mime=DOCX_MIME,
        disabled=not generated,
        key=f"download_{guest_id}",
        use_container_width=False,
    )

    word_button_label = (
        "✓ Opened in Word"
        if reviewed
        else "🟦 Open in Word 365"
    )

    if st.button(
        word_button_label,
        disabled=not generated,
        key=f"word_{guest_id}",
        use_container_width=False,
    ):
        try:
            word_url = _open_word_365_experience(guest, generated_path)

            opened_at = datetime.now().strftime("%I:%M %p").lstrip("0")
            st.session_state.word_opened[guest_id] = True
            st.session_state.setdefault("word_opened_at", {})[guest_id] = opened_at
            st.session_state.setdefault("word_urls", {})[guest_id] = word_url

            add_activity(
                guest_id,
                f"Document opened in Word 365 at {opened_at}",
            )

            st.toast("Document opened in Microsoft Word.", icon="🟦")
            st.rerun()

        except (ValueError, KeyError, OSError) as exc:
            st.error(f"Could not open the document in Word 365: {exc}")

    if reviewed:
        opened_at = st.session_state.get("word_opened_at", {}).get(guest_id)
        if opened_at:
            st.markdown(
                f'<div class="word-opened-meta">'
                f'<span>✓</span> Last opened today at {opened_at}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if st.button(
        "📧 Send Email",
        disabled=not (generated and reviewed and guest.get("email")),
        key=f"email_{guest_id}",
        use_container_width=False,
    ):
        try:
            steps = [
                ("Connecting to Outlook...", 20, 0.40),
                ("Preparing email message...", 45, 0.40),
                ("Attaching guest document...", 70, 0.45),
                ("Sending email...", 92, 0.35),
                ("Confirming delivery...", 98, 0.25),
            ]

            email_sent, status_placeholder, progress_bar = _show_progress(
                steps,
                action=lambda: send_guest_email(guest),
            )

            if email_sent:
                st.session_state.email_sent[guest_id] = True
                add_activity(
                    guest_id,
                    f"Email sent to {guest['email']}",
                )

                _finish_progress(
                    status_placeholder,
                    progress_bar,
                    "Email sent successfully.",
                    success_icon="📧",
                )

                st.toast("Email delivered.", icon="📧")
                st.rerun()
            else:
                progress_bar.empty()
                status_placeholder.empty()
                st.error("The email service could not send the message.")

        except (ValueError, KeyError, OSError) as exc:
            st.error(f"Could not send the email: {exc}")

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
