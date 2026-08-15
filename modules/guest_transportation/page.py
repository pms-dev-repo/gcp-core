from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from core.config import get_active_client_code, load_client_config
from services.database import DatabaseConfigurationError
from services.guest_transportation_service import (
    load_transportation_guests,
    save_transportation_assignment,
)


TRANSFER_STATUSES = (
    "Pending",
    "Assigned",
    "Confirmed",
    "Guest Contacted",
    "Driver En Route",
    "Guest Picked Up",
    "Completed",
    "Cancelled",
)

TRANSFER_TYPES = (
    "Airport pickup",
    "Airport drop-off",
    "Hotel transfer",
    "Private car",
    "Taxi",
    "Shuttle",
    "None",
)

VEHICLE_TYPES = (
    "Not assigned",
    "Sedan",
    "SUV",
    "Van",
    "Luxury vehicle",
    "Minibus",
    "Coach",
)

DATE_FORMATS = ("%b %d, %Y", "%Y-%m-%d", "%d %B %Y")


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _direction(guest: dict[str, Any]) -> str:
    movement = str(guest.get("movement") or "").strip().lower()
    return "Arrival" if movement in {"arrival", "arrivals"} else "Departure"


def _movement_date(guest: dict[str, Any]) -> date | None:
    stay = guest.get("stay", {}) or {}
    if _direction(guest) == "Arrival":
        return _parse_date(stay.get("arrival_date"))
    return _parse_date(stay.get("departure_date"))


def _pax(guest: dict[str, Any]) -> int:
    stay = guest.get("stay", {}) or {}
    return int(stay.get("adults") or 0) + int(stay.get("children") or 0)


def _default_record(guest: dict[str, Any]) -> dict[str, Any]:
    transport = guest.get("transport", {}) or {}
    raw_type = str(transport.get("transfer") or "None").strip()

    normalized_type = next(
        (
            item
            for item in TRANSFER_TYPES
            if item.casefold() == raw_type.casefold()
        ),
        raw_type if raw_type else "None",
    )

    record = {
        "guest_id": str(guest.get("id")),
        "status": "Pending" if normalized_type != "None" else "Pending",
        "transfer_type": normalized_type,
        "pickup_time": str(transport.get("eta") or ""),
        "flight": str(transport.get("flight") or ""),
        "pickup_location": str(transport.get("pickup_location") or ""),
        "destination": str(transport.get("destination") or ""),
        "vehicle_type": "Not assigned",
        "vehicle": "",
        "driver": "",
        "driver_phone": "",
        "notes": "",
        "updated_at": None,
    }
    assignment = guest.get("transport_assignment", {}) or {}
    for key in record:
        if key in assignment and assignment[key] is not None:
            record[key] = assignment[key]
    return record


def _store_key(client_code: str) -> str:
    return f"guest_transportation_records_{client_code}"


def _records(client_code: str) -> dict[str, dict[str, Any]]:
    key = _store_key(client_code)
    st.session_state.setdefault(key, {})
    return st.session_state[key]


def _record_for_guest(
    client_code: str,
    guest: dict[str, Any],
) -> dict[str, Any]:
    records = _records(client_code)
    guest_id = str(guest.get("id"))

    if guest_id not in records:
        records[guest_id] = _default_record(guest)

    return records[guest_id]


def _save_record(
    client_code: str,
    guest: dict[str, Any],
    payload: dict[str, Any],
) -> None:
    records = _records(client_code)
    guest_id = str(guest.get("id"))
    saved = save_transportation_assignment(client_code, guest, payload)
    records[guest_id] = {
        **records.get(guest_id, {}),
        **payload,
        "updated_at": saved.get("updated_at")
        or datetime.now().isoformat(timespec="seconds"),
    }


def _status_badge(status: str) -> str:
    palette = {
        "Pending": ("#FFF7ED", "#C2410C"),
        "Assigned": ("#EFF6FF", "#1D4ED8"),
        "Confirmed": ("#ECFDF5", "#047857"),
        "Guest Contacted": ("#F5F3FF", "#6D28D9"),
        "Driver En Route": ("#FEF3C7", "#92400E"),
        "Guest Picked Up": ("#E0F2FE", "#0369A1"),
        "Completed": ("#ECFDF5", "#047857"),
        "Cancelled": ("#FEF2F2", "#B91C1C"),
    }
    bg, fg = palette.get(status, ("#F3F4F6", "#4B5563"))
    return (
        f'<span style="display:inline-block;padding:4px 10px;'
        f'border-radius:999px;background:{bg};color:{fg};'
        f'font-size:11px;font-weight:700">{status}</span>'
    )


def _matches(
    guest: dict[str, Any],
    record: dict[str, Any],
    search: str,
) -> bool:
    if not search:
        return True

    needle = search.casefold()
    values = (
        guest.get("full_name"),
        guest.get("confirmation_number"),
        guest.get("room"),
        guest.get("email"),
        record.get("flight"),
        record.get("driver"),
        record.get("vehicle"),
    )
    return any(needle in str(value or "").casefold() for value in values)


def _render_metrics(
    guests: list[dict[str, Any]],
    client_code: str,
) -> None:
    records = [_record_for_guest(client_code, guest) for guest in guests]

    total = len(records)
    pickups = sum(
        1
        for record in records
        if "pickup" in str(record.get("transfer_type") or "").casefold()
    )
    dropoffs = sum(
        1
        for record in records
        if "drop" in str(record.get("transfer_type") or "").casefold()
    )
    pending = sum(
        1
        for record in records
        if record.get("status") in {"Pending", "Assigned"}
    )
    confirmed = sum(
        1
        for record in records
        if record.get("status") in {
            "Confirmed",
            "Guest Contacted",
            "Driver En Route",
            "Guest Picked Up",
        }
    )
    completed = sum(
        1 for record in records if record.get("status") == "Completed"
    )

    columns = st.columns(6)
    metrics = (
        ("Transfers", total),
        ("Pickups", pickups),
        ("Drop-offs", dropoffs),
        ("Pending", pending),
        ("Confirmed", confirmed),
        ("Completed", completed),
    )
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value)


def _render_filters(
    guests: list[dict[str, Any]],
    client_code: str,
) -> tuple[date | None, str, str, str]:
    available_dates = sorted(
        {
            movement_date
            for guest in guests
            if (movement_date := _movement_date(guest)) is not None
        }
    )

    default_date = available_dates[0] if available_dates else date.today()

    row1 = st.columns([1.1, 1, 1, 1.7])
    selected_date = row1[0].date_input(
        "Operational date",
        value=st.session_state.get(
            "transport_selected_date",
            default_date,
        ),
        key="transport_selected_date",
    )
    direction_filter = row1[1].selectbox(
        "Direction",
        ("All", "Arrival", "Departure"),
        key="transport_direction_filter",
    )
    status_filter = row1[2].selectbox(
        "Status",
        ("All",) + TRANSFER_STATUSES,
        key="transport_status_filter",
    )
    search = row1[3].text_input(
        "Search",
        placeholder="Guest, room, flight, driver or vehicle",
        key="transport_search",
    )

    return selected_date, direction_filter, status_filter, search


def _filtered_guests(
    guests: list[dict[str, Any]],
    client_code: str,
    selected_date: date | None,
    direction_filter: str,
    status_filter: str,
    search: str,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for guest in guests:
        record = _record_for_guest(client_code, guest)

        if selected_date and _movement_date(guest) != selected_date:
            continue
        if direction_filter != "All" and _direction(guest) != direction_filter:
            continue
        if status_filter != "All" and record.get("status") != status_filter:
            continue
        if not _matches(guest, record, search):
            continue

        result.append(guest)

    result.sort(
        key=lambda guest: (
            str(_record_for_guest(client_code, guest).get("pickup_time") or ""),
            str(guest.get("full_name") or ""),
        )
    )
    return result


def _render_transfer_list(
    guests: list[dict[str, Any]],
    client_code: str,
) -> None:
    if not guests:
        st.info("No transportation records match the current filters.")
        return

    with st.container(height=680, border=False):
        for guest in guests:
            guest_id = str(guest.get("id"))
            record = _record_for_guest(client_code, guest)
            selected = (
                str(st.session_state.get("transport_selected_guest_id") or "")
                == guest_id
            )

            with st.container(border=True):
                top_left, top_right = st.columns([0.72, 0.28])
                top_left.markdown(
                    f"**{guest.get('full_name', 'Unknown guest')}**"
                )
                top_right.markdown(
                    _status_badge(str(record.get("status") or "Pending")),
                    unsafe_allow_html=True,
                )

                st.caption(
                    f"{_direction(guest)} · "
                    f"{record.get('pickup_time') or 'Time TBA'} · "
                    f"Flight {record.get('flight') or '—'} · "
                    f"Room {guest.get('room') or 'TBA'} · "
                    f"{_pax(guest)} pax"
                )

                if st.button(
                    "Selected" if selected else "Manage transfer",
                    key=f"transport_open_{guest_id}",
                    type="primary" if selected else "secondary",
                    disabled=selected,
                    use_container_width=True,
                ):
                    st.session_state.transport_selected_guest_id = guest_id
                    st.rerun()


def _render_transfer_editor(
    guest: dict[str, Any],
    client_code: str,
) -> None:
    guest_id = str(guest.get("id"))
    record = _record_for_guest(client_code, guest)
    stay = guest.get("stay", {}) or {}

    st.markdown("### Transfer details")

    with st.container(border=True):
        detail_left, detail_right = st.columns(2)
        detail_left.write(f"**Guest:** {guest.get('full_name', '—')}")
        detail_left.write(
            f"**Confirmation:** {guest.get('confirmation_number', '—')}"
        )
        detail_left.write(f"**Room:** {guest.get('room') or 'TBA'}")
        detail_left.write(f"**Passengers:** {_pax(guest)}")

        detail_right.write(f"**Direction:** {_direction(guest)}")
        detail_right.write(
            f"**Date:** {_movement_date(guest) or '—'}"
        )
        detail_right.write(
            f"**Arrival:** {stay.get('arrival_date', '—')}"
        )
        detail_right.write(
            f"**Departure:** {stay.get('departure_date', '—')}"
        )

    with st.form(f"transport_editor_{guest_id}"):
        row1 = st.columns(2)
        status = row1[0].selectbox(
            "Status",
            TRANSFER_STATUSES,
            index=TRANSFER_STATUSES.index(
                record.get("status")
                if record.get("status") in TRANSFER_STATUSES
                else "Pending"
            ),
        )
        transfer_type_options = list(TRANSFER_TYPES)
        current_transfer_type = str(
            record.get("transfer_type") or "None"
        )
        if current_transfer_type not in transfer_type_options:
            transfer_type_options.append(current_transfer_type)

        transfer_type = row1[1].selectbox(
            "Transfer type",
            transfer_type_options,
            index=transfer_type_options.index(current_transfer_type),
        )

        row2 = st.columns(2)
        pickup_time = row2[0].text_input(
            "Pickup / expected time",
            value=str(record.get("pickup_time") or ""),
            placeholder="10:30 AM",
        )
        flight = row2[1].text_input(
            "Flight number",
            value=str(record.get("flight") or ""),
        )

        row3 = st.columns(2)
        pickup_location = row3[0].text_input(
            "Pickup location",
            value=str(record.get("pickup_location") or ""),
            placeholder="JFK Terminal 4",
        )
        destination = row3[1].text_input(
            "Destination",
            value=str(record.get("destination") or ""),
            placeholder="GCP Hotel",
        )

        row4 = st.columns(2)
        vehicle_type = row4[0].selectbox(
            "Vehicle type",
            VEHICLE_TYPES,
            index=VEHICLE_TYPES.index(
                record.get("vehicle_type")
                if record.get("vehicle_type") in VEHICLE_TYPES
                else "Not assigned"
            ),
        )
        vehicle = row4[1].text_input(
            "Vehicle / license plate",
            value=str(record.get("vehicle") or ""),
        )

        row5 = st.columns(2)
        driver = row5[0].text_input(
            "Driver",
            value=str(record.get("driver") or ""),
        )
        driver_phone = row5[1].text_input(
            "Driver phone",
            value=str(record.get("driver_phone") or ""),
        )

        notes = st.text_area(
            "Operational notes",
            value=str(record.get("notes") or ""),
            height=110,
        )

        submitted = st.form_submit_button(
            "Save transportation details",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        try:
            _save_record(
                client_code,
                guest,
                {
                    "status": status,
                    "transfer_type": transfer_type,
                    "pickup_time": pickup_time.strip(),
                    "flight": flight.strip(),
                    "pickup_location": pickup_location.strip(),
                    "destination": destination.strip(),
                    "vehicle_type": vehicle_type,
                    "vehicle": vehicle.strip(),
                    "driver": driver.strip(),
                    "driver_phone": driver_phone.strip(),
                    "notes": notes.strip(),
                },
            )
        except Exception as exc:
            st.error(f"Transportation details could not be saved: {exc}")
        else:
            st.toast("Transportation details saved in Supabase.", icon="✅")
            st.rerun()

    if record.get("updated_at"):
        st.caption(f"Last updated: {record['updated_at']}")


def _render_operational_table(
    guests: list[dict[str, Any]],
    client_code: str,
) -> None:
    st.markdown("### Operational transportation board")

    rows: list[dict[str, Any]] = []
    for guest in guests:
        record = _record_for_guest(client_code, guest)
        rows.append(
            {
                "Time": record.get("pickup_time"),
                "Direction": _direction(guest),
                "Guest": guest.get("full_name"),
                "Confirmation": guest.get("confirmation_number"),
                "Room": guest.get("room"),
                "Pax": _pax(guest),
                "Flight": record.get("flight"),
                "Transfer": record.get("transfer_type"),
                "Vehicle": record.get("vehicle") or record.get("vehicle_type"),
                "Driver": record.get("driver"),
                "Status": record.get("status"),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        height=min(520, 38 + len(rows) * 35),
    )


def render() -> None:
    client_code = get_active_client_code()
    config = load_client_config(client_code)
    client = config.get("client", {})
    hotel_name = str(client.get("name") or "Property")
    transportation_config = config.get("guest_transportation", {}) or {}
    data_client_code = str(
        transportation_config.get("data_client_code") or client_code
    )
    try:
        transport_guests = load_transportation_guests(data_client_code)
    except DatabaseConfigurationError as exc:
        st.error(f"Supabase is not configured: {exc}")
        return
    except Exception as exc:
        st.error(f"Transportation data could not be loaded from Supabase: {exc}")
        return

    st.markdown("# Guest Transportation")
    st.caption(
        f"Daily transfer planning and operational control · {hotel_name} · Live Supabase data"
    )

    _render_metrics(transport_guests, data_client_code)

    st.markdown("---")
    selected_date, direction_filter, status_filter, search = _render_filters(
        transport_guests,
        data_client_code,
    )

    filtered = _filtered_guests(
        transport_guests,
        data_client_code,
        selected_date,
        direction_filter,
        status_filter,
        search,
    )

    if filtered:
        selected_id = str(
            st.session_state.get("transport_selected_guest_id") or ""
        )
        available_ids = {str(guest.get("id")) for guest in filtered}
        if selected_id not in available_ids:
            st.session_state.transport_selected_guest_id = str(
                filtered[0].get("id")
            )

    list_col, detail_col = st.columns([0.39, 0.61], gap="large")

    with list_col:
        st.markdown("### Transfers")
        _render_transfer_list(filtered, data_client_code)

    with detail_col:
        selected_guest_id = str(
            st.session_state.get("transport_selected_guest_id") or ""
        )
        selected_guest = next(
            (
                guest
                for guest in filtered
                if str(guest.get("id")) == selected_guest_id
            ),
            None,
        )

        if selected_guest:
            _render_transfer_editor(selected_guest, data_client_code)
        else:
            st.info("Select a transfer to manage its operational details.")

    st.markdown("---")
    _render_operational_table(filtered, data_client_code)
