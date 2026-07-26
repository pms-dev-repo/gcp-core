from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
import zipfile

import streamlit as st

from components.document_panel import render_document_panel
from components.guest_summary import render_guest_summary
from components.history import render_history
from components.workflow import render_workflow
from services.document_service import (
    generate_bulk_documents,
    generate_bulk_pdfs,
)
from services.email_service import send_bulk_emails
from services.guest_service import get_guest_by_id
from utils.state import (
    add_activity,
    clear_bulk_selection,
    get_selected_guest_ids,
)


def _get_bulk_guests(guests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_ids = get_selected_guest_ids()
    return [guest for guest in guests if guest["id"] in selected_ids]


def _path_exists(path_value: Any) -> bool:
    if not path_value:
        return False
    try:
        return Path(path_value).is_file()
    except (TypeError, OSError):
        return False


def _build_bulk_pdf_zip(
    selected_guests: list[dict[str, Any]],
) -> tuple[bytes | None, int]:
    buffer = BytesIO()
    added = 0

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for guest in selected_guests:
            guest_id = guest["id"]
            pdf_value = st.session_state.generated_pdfs.get(guest_id)

            if not _path_exists(pdf_value):
                continue

            pdf_path = Path(pdf_value)
            guest_name = (
                guest.get("full_name")
                or guest.get("confirmation_number")
                or str(guest_id)
            )
            safe_name = "".join(
                char if char.isalnum() or char in {" ", "-", "_"} else "_"
                for char in str(guest_name)
            ).strip().replace(" ", "_")

            confirmation = guest.get("confirmation_number") or guest_id
            archive_name = (
                f"{safe_name}_{confirmation}.pdf"
                if safe_name
                else f"{confirmation}.pdf"
            )

            archive.writestr(archive_name, pdf_path.read_bytes())
            added += 1

    if added == 0:
        return None, 0

    buffer.seek(0)
    return buffer.getvalue(), added


def _render_bulk_table(selected_guests: list[dict[str, Any]]) -> None:
    generated_documents = st.session_state.generated_documents
    generated_pdfs = st.session_state.generated_pdfs
    email_sent = st.session_state.email_sent

    header_cols = st.columns([2.2, 1.2, 0.8, 1, 1, 1.2, 1.25], gap="small")
    headers = [
        "Guest",
        "Confirmation",
        "Room",
        "Letter",
        "PDF",
        "Status",
        "Download",
    ]
    for column, label in zip(header_cols, headers):
        column.markdown(f"**{label}**")

    st.divider()

    for guest in selected_guests:
        guest_id = guest["id"]
        has_email = bool(guest.get("email"))
        has_docx = _path_exists(generated_documents.get(guest_id))
        has_pdf = _path_exists(generated_pdfs.get(guest_id))
        was_sent = bool(email_sent.get(guest_id))

        if was_sent:
            status = "Sent"
        elif not has_docx:
            status = "Waiting for letter"
        elif not has_pdf:
            status = "Waiting for PDF"
        elif not has_email:
            status = "Missing email"
        else:
            status = "Ready to send"

        row_cols = st.columns([2.2, 1.2, 0.8, 1, 1, 1.2, 1.25], gap="small")
        row_cols[0].write(guest.get("full_name") or "Unknown guest")
        row_cols[1].write(guest.get("confirmation_number") or "—")
        row_cols[2].write(guest.get("room") or "—")
        row_cols[3].write("Available" if has_docx else "Pending")
        row_cols[4].write("Generated" if has_pdf else "Pending")
        row_cols[5].write(status)

        if has_pdf:
            pdf_path = Path(generated_pdfs[guest_id])
            try:
                pdf_bytes = pdf_path.read_bytes()
            except OSError as exc:
                row_cols[6].caption(f"Unavailable: {exc}")
            else:
                row_cols[6].download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    key=f"bulk_download_pdf_{guest_id}",
                    use_container_width=True,
                )
        else:
            row_cols[6].button(
                "Not Ready",
                key=f"bulk_pdf_not_ready_{guest_id}",
                disabled=True,
                use_container_width=True,
            )

        st.markdown(
            "<hr style='margin:0.35rem 0;border:none;border-top:1px solid #eceff3;'>",
            unsafe_allow_html=True,
        )


def _render_operation_result(
    title: str,
    results: dict[str, Any] | None,
) -> None:
    if not results:
        return

    generated = results.get("generated")
    sent = results.get("sent")
    failed = int(results.get("failed", 0))
    skipped = int(results.get("skipped", 0))

    if generated is not None:
        message = (
            f"{title}: {generated} completed, "
            f"{failed} failed, {skipped} skipped."
        )
    else:
        message = (
            f"{title}: {sent or 0} sent, "
            f"{failed} failed, {skipped} skipped."
        )

    if failed == 0 and skipped == 0:
        st.success(message)
    else:
        st.warning(message)

    details = results.get("results", [])
    if details:
        display_rows = [
            {
                key: value
                for key, value in item.items()
                if key not in {"guest_id", "Path"}
            }
            for item in details
        ]
        st.dataframe(display_rows, use_container_width=True, hide_index=True)


def _apply_document_results(results: dict[str, Any]) -> None:
    for item in results.get("results", []):
        guest_id = item["guest_id"]
        status = item.get("Status")
        path = item.get("Path")

        if status == "Generated" and path:
            st.session_state.generated_documents[guest_id] = path
            st.session_state.document_status[guest_id] = "Generated"
            st.session_state.generated_pdfs.pop(guest_id, None)
            st.session_state.email_sent[guest_id] = False
            add_activity(
                guest_id,
                "Guest letter generated through bulk communication.",
            )
        elif status == "Failed":
            add_activity(
                guest_id,
                f"Bulk letter generation failed: "
                f"{item.get('Message', 'Unknown error')}",
            )


def _apply_pdf_results(results: dict[str, Any]) -> None:
    for item in results.get("results", []):
        guest_id = item["guest_id"]
        status = item.get("Status")
        path = item.get("Path")

        if status == "Generated" and path:
            st.session_state.generated_pdfs[guest_id] = path
            st.session_state.email_sent[guest_id] = False
            add_activity(
                guest_id,
                "PDF generated through bulk communication.",
            )
        elif status == "Failed":
            add_activity(
                guest_id,
                f"Bulk PDF generation failed: "
                f"{item.get('Message', 'Unknown error')}",
            )


def _render_bulk_workspace(
    selected_guests: list[dict[str, Any]],
) -> None:
    selected_count = len(selected_guests)

    docx_ready_guests = [
        guest
        for guest in selected_guests
        if _path_exists(
            st.session_state.generated_documents.get(guest["id"])
        )
    ]
    pdf_ready_guests = [
        guest
        for guest in selected_guests
        if _path_exists(
            st.session_state.generated_pdfs.get(guest["id"])
        )
    ]
    send_ready_guests = [
        guest
        for guest in selected_guests
        if guest.get("email")
        and _path_exists(
            st.session_state.generated_documents.get(guest["id"])
        )
        and _path_exists(
            st.session_state.generated_pdfs.get(guest["id"])
        )
        and not st.session_state.email_sent.get(guest["id"], False)
    ]

    missing_email_count = sum(
        1 for guest in selected_guests if not guest.get("email")
    )

    st.markdown(
        '<div class="panel-title">Bulk Communication</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="muted">{selected_count} reservations selected.</div>',
        unsafe_allow_html=True,
    )

    total_col, letter_col, pdf_col, send_col = st.columns(4, gap="small")
    total_col.metric("Selected", selected_count)
    letter_col.metric("Letters Ready", len(docx_ready_guests))
    pdf_col.metric("PDF Ready", len(pdf_ready_guests))
    send_col.metric("Ready to Send", len(send_ready_guests))

    st.markdown("#### Review Selection")
    _render_bulk_table(selected_guests)

    zip_bytes, zip_count = _build_bulk_pdf_zip(selected_guests)
    zip_filename = (
        f"Guest_Letters_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.zip"
    )

    docx_col, pdf_col, download_col, send_col, clear_col = st.columns(
        [1, 1, 1, 1, 0.75],
        gap="small",
    )

    with docx_col:
        generate_documents_clicked = st.button(
            "Generate Guest Letters",
            key="bulk_generate_documents",
            use_container_width=True,
        )

    with pdf_col:
        generate_pdfs_clicked = st.button(
            f"Generate PDFs ({len(docx_ready_guests)})",
            key="bulk_generate_pdfs",
            use_container_width=True,
            disabled=len(docx_ready_guests) == 0,
        )

    with download_col:
        st.download_button(
            f"Download All PDFs ({zip_count})",
            data=zip_bytes or b"",
            file_name=zip_filename,
            mime="application/zip",
            key="bulk_download_all_pdfs",
            use_container_width=True,
            disabled=zip_bytes is None,
        )

    with send_col:
        send_clicked = st.button(
            f"Send Guest Letters ({len(send_ready_guests)})",
            key="send_bulk_emails",
            type="primary",
            use_container_width=True,
            disabled=len(send_ready_guests) == 0,
        )

    with clear_col:
        clear_clicked = st.button(
            "Clear Selection",
            key="clear_bulk_from_workspace",
            use_container_width=True,
        )

    if clear_clicked:
        clear_bulk_selection()
        st.session_state.selected_guest_id = None
        st.rerun()

    if missing_email_count:
        st.info(
            f"{missing_email_count} reservation(s) have no email. "
            "Their letters and PDFs can still be generated, but they "
            "will not be included in the email batch."
        )

    if generate_documents_clicked:
        with st.spinner("Generating guest letters..."):
            results = generate_bulk_documents(selected_guests)

        _apply_document_results(results)
        st.session_state.bulk_document_results = results
        st.session_state.bulk_pdf_results = None
        st.session_state.bulk_send_results = None
        st.rerun()

    if generate_pdfs_clicked:
        with st.spinner("Converting generated letters to PDF..."):
            results = generate_bulk_pdfs(
                selected_guests,
                st.session_state.generated_documents,
            )

        _apply_pdf_results(results)
        st.session_state.bulk_pdf_results = results
        st.session_state.bulk_send_results = None
        st.rerun()

    if send_clicked:
        with st.spinner("Sending guest letters..."):
            results = send_bulk_emails(send_ready_guests)

        for item in results.get("results", []):
            guest_id = item["guest_id"]
            item_status = item.get("Status")
            item_message = item.get("Message") or "Unknown error"

            if item_status == "Sent":
                st.session_state.email_sent[guest_id] = True
                add_activity(
                    guest_id,
                    "Email sent through bulk communication.",
                )
            elif item_status == "Failed":
                add_activity(
                    guest_id,
                    f"Bulk email failed: {item_message}",
                )

        st.session_state.bulk_send_results = results
        st.rerun()

    _render_operation_result(
        "Letter generation",
        st.session_state.get("bulk_document_results"),
    )
    _render_operation_result(
        "PDF generation",
        st.session_state.get("bulk_pdf_results"),
    )
    _render_operation_result(
        "Bulk email",
        st.session_state.get("bulk_send_results"),
    )


def render_workspace(guests: list[dict[str, Any]]) -> None:
    selected_guests = _get_bulk_guests(guests)

    if len(selected_guests) >= 2:
        _render_bulk_workspace(selected_guests)
        return

    if len(selected_guests) == 1:
        guest = selected_guests[0]
        st.session_state.selected_guest_id = guest["id"]
    else:
        guest = get_guest_by_id(
            guests,
            st.session_state.get("selected_guest_id"),
        )

    render_guest_summary(guest)

    content_col, action_col = st.columns([0.62, 0.38], gap="large")
    with content_col:
        render_document_panel(guest)
    with action_col:
        render_workflow(guest)
        render_history(guest)
