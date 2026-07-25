from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from services.document_service import (
    generate_guest_document,
    generate_guest_pdf,
    open_pdf_in_new_tab,
    read_generated_document,
)
from services.email_service import send_guest_email
from services.word_service import can_open_desktop_word, open_in_word_365
from utils.state import add_activity


DOCX_MIME = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def _show_progress(
    steps: list[tuple[str, int, float]],
    action: Callable[[], Any] | None = None,
) -> Any:
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


def _open_word_experience(
    guest: dict[str, Any],
    generated_path: Path,
) -> str:
    launcher = st.empty()

    stages = [
        ("Preparing your document", 18, "Connecting to Microsoft 365...", 0.45),
        ("Synchronizing document", 42, "Retrieving document...", 0.45),
        ("Authenticating", 68, "Validating Word session...", 0.45),
        ("Loading Word editor", 86, "Loading Microsoft Word tools...", 0.40),
        ("Opening document", 97, "Launching Microsoft Word...", 0.35),
    ]

    completed: list[str] = []

    for title, progress, active, delay in stages:
        with launcher.container(border=True):
            icon_col, title_col = st.columns([1, 7])
            with icon_col:
                st.markdown('<div class="m365-word-logo">W</div>', unsafe_allow_html=True)
            with title_col:
                st.markdown("**Microsoft 365**")
                st.caption("Microsoft Word")

            st.markdown(f"### {title}")
            st.progress(progress, text=f"{progress}%")

            for item in completed:
                st.markdown(f"✅ {item}")

            st.info(active, icon="🔄")

        completed.append(title)
        time.sleep(delay)

    word_url = open_in_word_365(generated_path)

    with launcher.container(border=True):
        icon_col, title_col = st.columns([1, 7])
        with icon_col:
            st.markdown('<div class="m365-word-logo">W</div>', unsafe_allow_html=True)
        with title_col:
            st.markdown("**Microsoft Word**")
            st.caption("Editing session")

        st.success("Document opened successfully.", icon="✅")
        st.progress(100, text="100%")
        st.markdown(f"**Document:** `{generated_path.name}`")
        st.caption("Edit the document and save it before generating the final PDF.")

    time.sleep(0.9)
    launcher.empty()
    return word_url


def _mark_word_reviewed(guest: dict[str, Any]) -> None:
    guest_id = guest["id"]
    opened_at = datetime.now().strftime("%I:%M %p").lstrip("0")

    st.session_state.word_opened[guest_id] = True
    st.session_state.setdefault("word_opened_at", {})[guest_id] = opened_at
    st.session_state.setdefault("pdf_generated", {})[guest_id] = False
    st.session_state.setdefault("generated_pdfs", {}).pop(guest_id, None)

    add_activity(
        guest_id,
        f"Document downloaded for Microsoft Word editing at {opened_at}",
    )


def render_workflow(guest: dict[str, Any]) -> None:
    guest_id = guest["id"]

    st.session_state.setdefault("pdf_generated", {})
    st.session_state.setdefault("generated_pdfs", {})

    generated_path_value = st.session_state.generated_documents.get(guest_id)
    generated_path = Path(generated_path_value) if generated_path_value else None
    generated = bool(generated_path and generated_path.exists())

    reviewed = st.session_state.word_opened.get(guest_id, False)
    pdf_path_value = st.session_state.generated_pdfs.get(guest_id)
    pdf_path = Path(pdf_path_value) if pdf_path_value else None
    pdf_ready = bool(pdf_path and pdf_path.exists())
    sent = st.session_state.email_sent.get(guest_id, False)

    with st.container(border=True):
        st.markdown('<span class="workflow-card-marker"></span>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title workflow-title">Workflow</div>', unsafe_allow_html=True)

        button_left, button_center, button_right = st.columns([1, 1.35, 1], gap="small")

        with button_center:
            if st.button(
                "✨ Generate Document",
                type="primary",
                key=f"generate_{guest_id}",
                use_container_width=True,
            ):
                try:
                    steps = [
                        ("Preparing Word template...", 15, 0.30),
                        ("Loading guest information...", 35, 0.35),
                        ("Replacing document placeholders...", 60, 0.40),
                        ("Creating Microsoft Word document...", 88, 0.30),
                        ("Finalizing document...", 96, 0.20),
                    ]

                    output_path, status_placeholder, progress_bar = _show_progress(
                        steps,
                        action=lambda: generate_guest_document(guest),
                    )

                    st.session_state.generated_documents[guest_id] = str(output_path)
                    st.session_state.document_status[guest_id] = True
                    st.session_state.word_opened[guest_id] = False
                    st.session_state.pdf_generated[guest_id] = False
                    st.session_state.generated_pdfs.pop(guest_id, None)
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

                except (FileNotFoundError, ValueError, KeyError, OSError, RuntimeError) as exc:
                    st.error(f"Could not generate the document: {exc}")

            try:
                docx_bytes = (
                    read_generated_document(generated_path)
                    if generated and generated_path
                    else b""
                )
            except OSError as exc:
                docx_bytes = b""
                st.error(f"Could not read the generated document: {exc}")

            desktop_word_available = can_open_desktop_word()

            st.markdown('<span class="word-action-marker"></span>', unsafe_allow_html=True)

            if desktop_word_available:
                if st.button(
                    "Edit in Microsoft Word" if not reviewed else "Edited in Microsoft Word",
                    disabled=not generated,
                    key=f"word_{guest_id}",
                    use_container_width=True,
                ):
                    try:
                        if generated_path is None:
                            raise FileNotFoundError("Generate the document first.")

                        word_url = _open_word_experience(guest, generated_path)
                        opened_at = datetime.now().strftime("%I:%M %p").lstrip("0")

                        st.session_state.word_opened[guest_id] = True
                        st.session_state.setdefault("word_opened_at", {})[guest_id] = opened_at
                        st.session_state.setdefault("word_urls", {})[guest_id] = word_url
                        st.session_state.pdf_generated[guest_id] = False
                        st.session_state.generated_pdfs.pop(guest_id, None)

                        add_activity(
                            guest_id,
                            f"Document opened for editing in Microsoft Word at {opened_at}",
                        )

                        st.toast("Document opened in Microsoft Word.", icon="✅")
                        st.rerun()

                    except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
                        st.error(f"Could not open the document in Word: {exc}")
            else:
                st.download_button(
                    "Edit in Microsoft Word" if not reviewed else "Edited in Microsoft Word",
                    data=docx_bytes,
                    file_name=generated_path.name if generated_path else "guest_letter.docx",
                    mime=DOCX_MIME,
                    disabled=not generated,
                    key=f"word_download_{guest_id}",
                    on_click=_mark_word_reviewed,
                    args=(guest,),
                    use_container_width=True,
                )
                if generated:
                    st.caption(
                        "Download the editable DOCX, open it in Microsoft Word, "
                        "save your changes, and then generate the final PDF."
                    )

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
                "📄 Open Final PDF",
                disabled=not (generated and reviewed),
                key=f"open_pdf_{guest_id}",
                use_container_width=True,
            ):
                try:
                    if generated_path is None:
                        raise FileNotFoundError("Generate the document first.")

                    steps = [
                        ("Reading the edited Word document...", 25, 0.25),
                        ("Converting with Microsoft Word...", 65, 0.35),
                        ("Preparing PDF preview...", 92, 0.25),
                        ("Opening PDF...", 98, 0.15),
                    ]

                    final_pdf, status_placeholder, progress_bar = _show_progress(
                        steps,
                        action=lambda: generate_guest_pdf(generated_path),
                    )

                    st.session_state.generated_pdfs[guest_id] = str(final_pdf)
                    st.session_state.pdf_generated[guest_id] = True

                    add_activity(
                        guest_id,
                        f"Final PDF generated and opened: {final_pdf.name}",
                    )

                    _finish_progress(
                        status_placeholder,
                        progress_bar,
                        "Final PDF generated successfully.",
                    )

                    open_pdf_in_new_tab(final_pdf)
                    st.toast("Final PDF opened in a new browser tab.", icon="📄")
                    st.rerun()

                except (FileNotFoundError, ValueError, OSError, RuntimeError) as exc:
                    st.error(f"Could not generate or open the final PDF: {exc}")

            if st.button(
                "📧 Send Email",
                disabled=not (pdf_ready and guest.get("email")),
                key=f"email_{guest_id}",
                use_container_width=True,
            ):
                try:
                    steps = [
                        ("Connecting to Outlook...", 20, 0.35),
                        ("Preparing email message...", 45, 0.35),
                        ("Attaching final PDF...", 70, 0.40),
                        ("Sending email...", 92, 0.30),
                        ("Confirming delivery...", 98, 0.20),
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

        st.markdown(
            '<div class="workflow-status-title">Communication Status</div>',
            unsafe_allow_html=True,
        )

        readiness = [
            ("Guest selected", True),
            ("Email available", bool(guest.get("email"))),
            ("Document generated", generated),
            ("Edited in Microsoft Word", reviewed),
            ("Final PDF generated", pdf_ready),
            ("Email sent", sent),
        ]

        for label, done in readiness:
            st.markdown(f"{'✅' if done else '○'} {label}")
