from __future__ import annotations

from datetime import date, datetime
from html import escape
from typing import Any

import streamlit as st

from core.config import get_active_client_code, load_client_config


SEGMENTS = ("Arrivals", "Departures", "In House")
DEFAULT_TEMPLATES = {
    "Arrivals": "Welcome {{first_name}}! We look forward to your arrival at {{hotel_name}}. Replying is not monitored.",
    "Departures": "Thank you for staying with us, {{first_name}}. We hope you enjoyed your visit to {{hotel_name}}. Replying is not monitored.",
    "In House": "Hello {{first_name}}, we hope you are enjoying your stay at {{hotel_name}}. For assistance, please contact the Front Desk. Replying is not monitored.",
}
OPT_OUT_FOOTER = "Text STOP to opt out."


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    for pattern in ("%b %d, %Y", "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _matches_segment(guest: dict[str, Any], segment: str, today: date) -> bool:
    movement = _normalize(guest.get("movement"))
    reservation_status = _normalize(guest.get("reservation_status"))
    if segment == "Arrivals":
        return movement in {"arrival", "arrivals"}
    if segment == "Departures":
        return movement in {"departure", "departures"}
    if reservation_status in {"in_house", "checked_in", "occupied"}:
        return True
    stay = guest.get("stay") or {}
    arrival = _parse_date(stay.get("arrival_date"))
    departure = _parse_date(stay.get("departure_date"))
    return bool(arrival and departure and arrival <= today < departure)


def _demo_phone(guest: dict[str, Any]) -> str:
    guest_id = str(guest.get("id") or guest.get("confirmation_number") or "guest")
    suffix = sum((index + 1) * ord(char) for index, char in enumerate(guest_id)) % 10_000
    return f"+1 246 555 {suffix:04d}"


def _recipient_phone(guest: dict[str, Any], allow_demo: bool) -> tuple[str, bool]:
    phone = str(guest.get("phone") or guest.get("mobile") or "").strip()
    if phone:
        return phone, False
    return (_demo_phone(guest), True) if allow_demo else ("", False)


def _personalize(template: str, guest: dict[str, Any], hotel_name: str) -> str:
    first_name = str(guest.get("first_name") or guest.get("full_name") or "Guest").split()[0]
    stay = guest.get("stay") or {}
    values = {
        "{{first_name}}": first_name,
        "{{hotel_name}}": hotel_name,
        "{{arrival_date}}": str(stay.get("arrival_date") or ""),
        "{{departure_date}}": str(stay.get("departure_date") or ""),
    }
    message = template
    for token, value in values.items():
        message = message.replace(token, value)
    return f"{message.strip()} {OPT_OUT_FOOTER}".strip()


def _init_state() -> None:
    st.session_state.setdefault("sms_opt_out_ids", set())
    st.session_state.setdefault("sms_demo_history", [])


def _metrics(total: int, eligible: int, opted_out: int, missing: int) -> None:
    for column, (label, value) in zip(
        st.columns(4),
        (("Guests in segment", total), ("Eligible recipients", eligible), ("Opted out", opted_out), ("Missing mobile", missing)),
    ):
        with column:
            st.metric(label, value)


def _opt_out_manager(guests: list[dict[str, Any]]) -> None:
    opt_out_ids: set[str] = st.session_state.sms_opt_out_ids
    with st.expander("Manage SMS consent and opt-outs"):
        st.caption("Demo only. In production, STOP requests would be processed automatically by the SMS provider and synchronized with the guest profile.")
        if not guests:
            st.info("No guests are available in this segment.")
            return
        guest_map = {str(guest["id"]): guest for guest in guests}
        selected_id = st.selectbox(
            "Guest",
            list(guest_map),
            format_func=lambda guest_id: str(guest_map[guest_id].get("full_name") or guest_id),
            key="sms_consent_guest",
        )
        is_opted_out = selected_id in opt_out_ids
        st.write(f"**Current status:** {'OPTED OUT' if is_opted_out else 'Eligible'}")
        if st.button("Restore SMS consent" if is_opted_out else "Mark as OPT OUT", key="sms_toggle_consent"):
            opt_out_ids.discard(selected_id) if is_opted_out else opt_out_ids.add(selected_id)
            st.session_state.sms_opt_out_ids = opt_out_ids
            st.rerun()


def _recipient_preview(guests: list[dict[str, Any]], allow_demo: bool, opt_out_ids: set[str]) -> None:
    st.markdown("### Recipient preview")
    st.caption("The first 12 matching guests are shown. Opted-out guests are always suppressed.")
    rows = []
    for guest in guests[:12]:
        guest_id = str(guest.get("id"))
        phone, is_demo = _recipient_phone(guest, allow_demo)
        status = "OPT OUT" if guest_id in opt_out_ids else ("Ready" if phone else "Missing mobile")
        rows.append({
            "Guest": guest.get("full_name", "Guest"),
            "Mobile": f"{phone} (demo)" if is_demo else phone,
            "Reservation": guest.get("confirmation_number", ""),
            "SMS status": status,
        })
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No guests match this reservation segment.")


def render(guests: list[dict[str, Any]]) -> None:
    _init_state()
    config = load_client_config(get_active_client_code())
    client = config.get("client") or {}
    sms_config = config.get("guest_sms") or {}
    hotel_name = str(client.get("name") or "the hotel")
    sender_name = str(sms_config.get("sender_name") or hotel_name)
    allow_demo = bool(sms_config.get("allow_demo_numbers", True))

    st.markdown("## Guest SMS")
    st.caption("Send reservation-based SMS campaigns · Demo mode · No messages leave GCP")
    st.markdown(
        f'<div class="sms-demo-banner"><strong>NO REPLY · {escape(sender_name)}</strong><span>Simulated workspace. Delivery, billing and carrier traffic are disabled.</span></div>',
        unsafe_allow_html=True,
    )

    segment = st.segmented_control("Reservation segment", SEGMENTS, default="Arrivals", key="sms_segment") or "Arrivals"
    matching = [guest for guest in guests if _matches_segment(guest, segment, date.today())]
    opt_out_ids: set[str] = st.session_state.sms_opt_out_ids
    eligible, missing = [], 0
    for guest in matching:
        phone, _ = _recipient_phone(guest, allow_demo)
        if not phone:
            missing += 1
        elif str(guest.get("id")) not in opt_out_ids:
            eligible.append(guest)
    opted_out = sum(str(guest.get("id")) in opt_out_ids for guest in matching)
    _metrics(len(matching), len(eligible), opted_out, missing)

    left, right = st.columns([0.56, 0.44], gap="large")
    with left:
        st.markdown("### Message template")
        template = st.text_area(
            "SMS content",
            value=DEFAULT_TEMPLATES[segment],
            height=150,
            key=f"sms_template_{segment}",
            help="Available fields: {{first_name}}, {{hotel_name}}, {{arrival_date}}, {{departure_date}}",
        )
        length = len(f"{template.strip()} {OPT_OUT_FOOTER}")
        st.caption(f"{length} characters · approximately {max(1, (length + 159) // 160)} SMS part(s) · The opt-out footer is added automatically.")
    with right:
        st.markdown("### Personalized preview")
        sample = eligible[0] if eligible else (matching[0] if matching else {})
        st.markdown(f'<div class="sms-phone-preview">{escape(_personalize(template, sample, hotel_name))}</div>', unsafe_allow_html=True)

    _opt_out_manager(matching)
    _recipient_preview(matching, allow_demo, opt_out_ids)
    st.divider()
    send_col, note_col = st.columns([0.32, 0.68], gap="large")
    with send_col:
        if st.button(f"Simulate send to {len(eligible):,} guests", type="primary", use_container_width=True, disabled=not eligible):
            st.session_state.sms_demo_history.insert(0, {
                "time": datetime.now().strftime("%d %b %Y · %I:%M %p"),
                "segment": segment,
                "recipients": len(eligible),
                "suppressed": opted_out + missing,
            })
            st.success(f"Demo completed: {len(eligible):,} eligible recipients, {opted_out + missing:,} suppressed. No SMS was sent.")
    with note_col:
        st.info("Production version: connect an approved provider, validate consent, process STOP automatically, enforce quiet hours and store an audit trail.")

    if st.session_state.sms_demo_history:
        st.markdown("### Demo activity")
        st.dataframe(st.session_state.sms_demo_history[:10], use_container_width=True, hide_index=True)

    st.markdown(
        """
        <style>
        .sms-demo-banner{display:flex;justify-content:space-between;gap:20px;align-items:center;padding:14px 18px;margin:4px 0 18px;border:1px solid #d8deea;border-left:4px solid #f2cf62;border-radius:8px;background:#f8f9fc;color:#30364c;font-size:12px}
        .sms-phone-preview{min-height:150px;padding:18px;border-radius:18px 18px 18px 4px;background:#eef1f7;border:1px solid #d8deea;color:#252a3b;font-size:14px;line-height:1.55;box-shadow:0 6px 18px rgba(48,54,76,.08)}
        @media(max-width:900px){.sms-demo-banner{align-items:flex-start;flex-direction:column;gap:4px}}
        </style>
        """,
        unsafe_allow_html=True,
    )
