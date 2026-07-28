from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

from core.config import get_default_client_code
from services.document_service import generate_guest_document, generate_guest_pdf
from services.email_service import send_guest_email
from services.guest_service import (
    filter_cancellations_by_date,
    filter_confirmations_by_arrival_date,
    get_available_cancellation_dates,
    get_available_confirmation_dates,
    load_guests,
)


def _init_state(guests: list[dict[str, Any]]) -> None:
    st.session_state.setdefault("confirmation_documents", {})
    st.session_state.setdefault("cancellation_documents", {})
    st.session_state.setdefault("confirmation_sent", set())
    st.session_state.setdefault("cancellation_sent", set())
    for guest in guests:
        communications = guest.get("communications", {})
        guest_id = guest.get("id")
        if communications.get("confirmation_letter") == "Sent":
            st.session_state.confirmation_sent.add(guest_id)
        if communications.get("cancellation_letter") == "Sent":
            st.session_state.cancellation_sent.add(guest_id)


def _status(guest: dict[str, Any], kind: str) -> str:
    guest_id = guest["id"]
    if kind == "confirmation":
        if guest_id in st.session_state.confirmation_sent:
            return "Sent"
        if guest_id in st.session_state.confirmation_documents:
            return "Generated"
        original = guest.get("communications", {}).get("confirmation_letter", "Pending")
    else:
        if guest_id in st.session_state.cancellation_sent:
            return "Sent"
        if guest_id in st.session_state.cancellation_documents:
            return "Generated"
        original = guest.get("communications", {}).get("cancellation_letter", "Pending")
    if not guest.get("email"):
        return "Missing Email"
    return original if original in {"Pending", "Generated", "Sent"} else "Pending"


def _metric_cards(guests: list[dict[str, Any]], kind: str) -> None:
    statuses = [_status(g, kind) for g in guests]
    columns = st.columns(4)
    labels = (
        ("New reservations" if kind == "confirmation" else "New cancellations", len(guests)),
        ("Generated", statuses.count("Generated")),
        ("Sent", statuses.count("Sent")),
        ("Pending", statuses.count("Pending") + statuses.count("Missing Email")),
    )
    for column, (label, value) in zip(columns, labels):
        with column:
            st.metric(label, value)


def _render_list(guests: list[dict[str, Any]], kind: str) -> None:
    if not guests:
        st.info("No records found for the selected date.")
        return

    selected_key = f"selected_{kind}_guest"
    valid_ids = {guest["id"] for guest in guests}
    if st.session_state.get(selected_key) not in valid_ids:
        st.session_state[selected_key] = guests[0]["id"]

    left, right = st.columns([0.42, 0.58], gap="large")
    with left:
        st.markdown("### Reservations")
        search = st.text_input("Search", key=f"search_{kind}", placeholder="Guest or confirmation number")
        normalized = search.strip().lower()
        shown = [g for g in guests if not normalized or normalized in str(g.get("full_name", "")).lower() or normalized in str(g.get("confirmation_number", "")).lower()]
        for guest in shown:
            status = _status(guest, kind)
            label = f"{guest.get('full_name', 'Guest')}  ·  {guest.get('confirmation_number', '')}  ·  {status}"
            if st.button(label, key=f"{kind}_{guest['id']}", use_container_width=True):
                st.session_state[selected_key] = guest["id"]
                st.rerun()

    selected = next(g for g in guests if g["id"] == st.session_state[selected_key])
    with right:
        _render_detail(selected, kind)


def _render_detail(guest: dict[str, Any], kind: str) -> None:
    stay = guest.get("stay", {})
    status = _status(guest, kind)
    title = "Confirmation letter" if kind == "confirmation" else "Cancellation letter"
    st.markdown(f"### {title}")
    st.caption(f"Status: {status}")

    a, b = st.columns(2)
    with a:
        st.write(f"**Guest:** {guest.get('full_name', '—')}")
        st.write(f"**Confirmation:** {guest.get('confirmation_number', '—')}")
        st.write(f"**Email:** {guest.get('email') or 'Missing email'}")
        st.write(f"**Language:** {guest.get('preferred_language', guest.get('template', {}).get('language', 'English'))}")
    with b:
        st.write(f"**Arrival:** {stay.get('arrival_date', '—')}")
        st.write(f"**Departure:** {stay.get('departure_date', '—')}")
        st.write(f"**Room type:** {guest.get('room_type', '—')}")
        if kind == "cancellation":
            st.write(f"**Cancelled:** {guest.get('cancellation_date', '—')}")
            st.write(f"**Reason:** {guest.get('cancellation_reason', '—')}")

    document_map = st.session_state.confirmation_documents if kind == "confirmation" else st.session_state.cancellation_documents
    guest_id = guest["id"]
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Generate DOCX", key=f"generate_{kind}_{guest_id}", use_container_width=True):
            try:
                path = generate_guest_document(guest, document_kind=kind)
                document_map[guest_id] = str(path)
                st.success("Letter generated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with c2:
        path_value = document_map.get(guest_id)
        if path_value and Path(path_value).is_file():
            path = Path(path_value)
            st.download_button("Download DOCX", path.read_bytes(), file_name=path.name, key=f"download_{kind}_{guest_id}", use_container_width=True)
        else:
            st.button("Download DOCX", disabled=True, key=f"download_disabled_{kind}_{guest_id}", use_container_width=True)
    with c3:
        if st.button("Send Email", key=f"send_{kind}_{guest_id}", use_container_width=True, disabled=not bool(document_map.get(guest_id))):
            if send_guest_email(guest):
                target = st.session_state.confirmation_sent if kind == "confirmation" else st.session_state.cancellation_sent
                target.add(guest_id)
                st.success("Email sent successfully.")
                st.rerun()
            else:
                st.error("The reservation does not have an email address.")

    path_value = document_map.get(guest_id)
    if path_value:
        if st.button("Generate PDF", key=f"pdf_{kind}_{guest_id}"):
            try:
                pdf_path = generate_guest_pdf(path_value)
                st.download_button("Download PDF", pdf_path.read_bytes(), file_name=pdf_path.name, key=f"pdf_download_{kind}_{guest_id}")
            except Exception as exc:
                st.error(str(exc))


def render() -> None:
    client_code = st.session_state.get("active_client_code", get_default_client_code())
    guests = load_guests(client_code)
    _init_state(guests)

    st.markdown("## Confirmation Letters")
    st.caption("Generate, review and send confirmation and cancellation letters.")

    confirmation_tab, cancellation_tab = st.tabs(["Confirmation", "Cancellation"])

    with confirmation_tab:
        dates = get_available_confirmation_dates(guests)
        if not dates:
            st.info("No arrival dates are available.")
        else:
            selected_date = st.selectbox("Arrival Date", dates, format_func=lambda value: value.strftime("%d %b %Y"), key="confirmation_arrival_date")
            filtered = filter_confirmations_by_arrival_date(guests, selected_date)
            _metric_cards(filtered, "confirmation")
            st.divider()
            _render_list(filtered, "confirmation")

    with cancellation_tab:
        dates = get_available_cancellation_dates(guests)
        if not dates:
            st.info("No cancellation dates are available.")
        else:
            selected_date = st.selectbox("Cancellation Date", dates, format_func=lambda value: value.strftime("%d %b %Y"), key="cancellation_date")
            filtered = filter_cancellations_by_date(guests, selected_date)
            _metric_cards(filtered, "cancellation")
            st.divider()
            _render_list(filtered, "cancellation")
