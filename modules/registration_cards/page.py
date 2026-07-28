from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from core.config import get_default_client_code, load_client_config
from services.email_service import send_registration_card_email
from services.guest_service import load_guests
from services.registration_card_service import (
    create_or_get_registration_card,
    list_registration_cards,
)


def _status_badge(status: str) -> str:
    colors = {
        "Ready": ("#ECFDF5", "#047857"),
        "Generated": ("#EFF6FF", "#1D4ED8"),
        "Sent": ("#FFF7ED", "#C2410C"),
        "Opened": ("#F5F3FF", "#6D28D9"),
        "Signed": ("#ECFDF5", "#047857"),
    }
    background, foreground = colors.get(status, ("#F3F4F6", "#4B5563"))
    return (
        f'<span style="display:inline-block;padding:3px 9px;'
        f'border-radius:999px;background:{background};color:{foreground};'
        f'font-size:11px;font-weight:700">{status}</span>'
    )


def _matches(guest: dict[str, Any], term: str) -> bool:
    if not term:
        return True

    needle = term.casefold()
    values = (
        guest.get("full_name"),
        guest.get("confirmation_number"),
        guest.get("email"),
        guest.get("room"),
        guest.get("document_number"),
    )
    return any(needle in str(value or "").casefold() for value in values)


def _cards_by_guest(
    cards: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build an in-memory lookup and avoid one Supabase query per guest."""
    lookup: dict[str, dict[str, Any]] = {}
    for card in cards:
        guest_id = str(card.get("guest_id") or "")
        if guest_id and guest_id not in lookup:
            lookup[guest_id] = card
    return lookup


def _render_guest_list(
    guests: list[dict[str, Any]],
    cards_by_guest: dict[str, dict[str, Any]],
) -> None:
    st.markdown("### Upcoming arrivals")

    search = st.text_input(
        "Search reservation",
        placeholder="Guest, confirmation, room, email or document",
        label_visibility="collapsed",
    )

    arrivals = [
        guest
        for guest in guests
        if guest.get("movement") == "Arrivals" and _matches(guest, search)
    ]

    if not arrivals:
        st.info("No arrivals match the current search.")
        return

    with st.container(height=660, border=False):
        for guest in arrivals:
            guest_id = str(guest["id"])
            selected = (
                st.session_state.get("registration_selected_guest_id")
                == guest_id
            )
            card = cards_by_guest.get(guest_id)
            status = str(card.get("status")) if card else "Ready"
            stay = guest.get("stay", {})

            with st.container(border=True):
                st.markdown(
                    f"**{guest.get('full_name', 'Unknown guest')}**"
                )
                st.caption(
                    f"Confirmation {guest.get('confirmation_number', '—')} · "
                    f"Room {guest.get('room') or 'TBA'} · "
                    f"Arrival {stay.get('arrival_date', '—')}"
                )
                st.markdown(_status_badge(status), unsafe_allow_html=True)

                if st.button(
                    "Selected" if selected else "Open Registration Card",
                    key=f"registration_open_{guest_id}",
                    type="primary" if selected else "secondary",
                    disabled=selected,
                    use_container_width=True,
                ):
                    st.session_state.registration_selected_guest_id = guest_id
                    st.rerun()


def _render_summary(
    guest: dict[str, Any],
    cards_by_guest: dict[str, dict[str, Any]],
) -> None:
    guest_id = str(guest["id"])
    card = cards_by_guest.get(guest_id)
    stay = guest.get("stay", {})

    st.markdown("### Registration Card")
    st.caption(
        "Generate a unique card, send the secure link, and capture the "
        "guest's completed form and signature."
    )

    with st.container(border=True):
        left, right = st.columns(2)
        left.metric(
            "Correlative",
            (
                card.get("registration_card_number", "Assigned on generation")
                if card
                else "Assigned on generation"
            ),
        )
        right.metric("Status", card.get("status", "Ready") if card else "Ready")

        st.markdown("---")
        detail_left, detail_right = st.columns(2)

        detail_left.write(f"**Guest:** {guest.get('full_name', '—')}")
        detail_left.write(
            f"**Confirmation:** {guest.get('confirmation_number', '—')}"
        )
        detail_left.write(f"**Email:** {guest.get('email') or 'Missing'}")
        detail_left.write(
            f"**Document:** {guest.get('document_type', '—')} "
            f"{guest.get('document_number', '—')}"
        )

        detail_right.write(f"**Arrival:** {stay.get('arrival_date', '—')}")
        detail_right.write(f"**Departure:** {stay.get('departure_date', '—')}")
        detail_right.write(f"**Room type:** {guest.get('room_type', '—')}")
        detail_right.write(
            f"**Guests:** {stay.get('adults', 0)} adult(s), "
            f"{stay.get('children', 0)} child(ren)"
        )

    with st.container(border=True):
        st.markdown("### Workflow")

        if st.button(
            "1. Generate Registration Card",
            key=f"registration_generate_{guest_id}",
            type="primary",
            disabled=card is not None,
            use_container_width=True,
        ):
            with st.spinner("Generating registration card..."):
                created = create_or_get_registration_card(guest)

            st.toast(
                f"{created['registration_card_number']} generated.",
                icon="✅",
            )
            st.rerun()

        if card:
            st.text_input(
                "Guest form link",
                value=card["public_url"],
                disabled=True,
                key=f"registration_link_{guest_id}",
            )

            if st.button(
                "2. Send Form by Email",
                key=f"registration_send_{guest_id}",
                disabled=(
                    not guest.get("email")
                    or card.get("status") == "Signed"
                ),
                use_container_width=True,
            ):
                with st.spinner("Sending guest form..."):
                    sent = send_registration_card_email(guest, card)

                if sent:
                    st.success(
                        f"Demo email sent to {guest['email']}.",
                        icon="📧",
                    )
                    st.rerun()
                else:
                    st.error("The guest does not have an email address.")

            st.link_button(
                "3. Open Guest Form",
                card["public_url"],
                use_container_width=True,
            )

            if card.get("status") == "Signed":
                response = card.get("response", {})
                st.success(
                    "The guest completed and signed this registration card.",
                    icon="✅",
                )
                st.write(
                    f"**Signed by:** {response.get('typed_signature', '—')}"
                )
                st.write(f"**Signed at:** {response.get('signed_at', '—')}")
                st.write(
                    f"**Country:** {response.get('country', '—')} · "
                    f"**Document:** {response.get('document_type', '—')} "
                    f"{response.get('document_number', '—')}"
                )
            else:
                st.info(
                    "Waiting for the guest to complete and sign the form."
                )


def _render_history(cards: list[dict[str, Any]]) -> None:
    st.markdown("### Recent Registration Cards")

    if not cards:
        st.caption("No registration cards have been generated yet.")
        return

    rows = []
    for card in cards[:20]:
        guest = card.get("guest", {})
        rows.append(
            {
                "Correlative": card.get("registration_card_number"),
                "Guest": guest.get("full_name"),
                "Confirmation": card.get("confirmation_number"),
                "Status": card.get("status"),
                "Generated": card.get("generated_at"),
                "Sent": card.get("sent_at"),
                "Signed": card.get("completed_at"),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def render() -> None:
    st.markdown("# Registration Cards")
    st.caption(
        "Digital pre-registration cards for Accor Peru · "
        f"{datetime.now().strftime('%d %B %Y')}"
    )

    client_code = str(
        st.session_state.get(
            "active_client_code",
            get_default_client_code(),
        )
    )
    load_client_config(client_code)
    guests = load_guests(client_code)

    arrivals = [
        guest for guest in guests if guest.get("movement") == "Arrivals"
    ]

    st.session_state.setdefault(
        "registration_selected_guest_id",
        str(arrivals[0]["id"]) if arrivals else None,
    )

    selected_guest = next(
        (
            guest
            for guest in arrivals
            if str(guest.get("id"))
            == str(st.session_state.registration_selected_guest_id)
        ),
        None,
    )

    # One Supabase query per page render instead of one query per guest.
    cards = list_registration_cards()
    cards_lookup = _cards_by_guest(cards)

    list_col, detail_col = st.columns([0.38, 0.62], gap="large")

    with list_col:
        _render_guest_list(guests, cards_lookup)

    with detail_col:
        if selected_guest:
            _render_summary(selected_guest, cards_lookup)
        else:
            st.info("Select an arrival to prepare its registration card.")

    st.markdown("---")
    _render_history(cards)
