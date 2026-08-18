from __future__ import annotations

import hashlib
from typing import Any

from services.database import get_reports_supabase, get_supabase


ARRIVALS_VIEW = "vw_daily_arrivals_transportation"
DEPARTURES_VIEW = "vw_daily_departures_transportation"
ASSIGNMENTS_TABLE = "guest_transportation_assignments"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _record_key(direction: str, row: dict[str, Any]) -> str:
    movement_date = row.get("arrival_date" if direction == "Arrival" else "departure_date")
    identity = row.get("confirmation_no") or row.get("guest_name")
    raw = "|".join(
        (
            _text(row.get("client_code")),
            direction,
            _text(movement_date),
            _text(identity).casefold(),
            _text(row.get("room_no")),
        )
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _airport_label(row: dict[str, Any], prefix: str) -> str:
    name = _text(row.get(f"{prefix}_airport"))
    code = _text(row.get(f"{prefix}_iata"))
    if name and code:
        return f"{name} ({code})"
    return name or code


def _map_arrival(row: dict[str, Any]) -> dict[str, Any]:
    has_transfer = bool(_text(row.get("transport_direction")))
    record_key = _record_key("Arrival", row)
    return {
        "id": record_key,
        "full_name": _text(row.get("guest_name")) or "Unknown guest",
        "confirmation_number": row.get("confirmation_no") or "",
        "room": row.get("room_no") or "",
        "movement": "Arrivals",
        "reservation_status": _text(row.get("reservation_status")),
        "stay": {
            "arrival_date": row.get("arrival_date"),
            "departure_date": row.get("departure_date"),
            "adults": row.get("adults") or 0,
            "children": row.get("children") or 0,
        },
        "transport": {
            "transfer": "Airport pickup" if has_transfer else "None",
            "eta": _text(row.get("transport_time") or row.get("arrival_time")),
            "flight": _text(row.get("transport_flight") or row.get("arrival_carrier_code")),
            "pickup_location": _airport_label(row, "destination"),
            "destination": "",
            "source_type": _text(row.get("transport_type")),
        },
    }


def _map_departure(row: dict[str, Any]) -> dict[str, Any]:
    record_key = _record_key("Departure", row)
    return {
        "id": record_key,
        "full_name": _text(row.get("guest_name")) or "Unknown guest",
        "confirmation_number": "",
        "room": row.get("room_no") or "",
        "movement": "Departures",
        "reservation_status": _text(row.get("reservation_status")),
        "stay": {
            "arrival_date": row.get("arrival_date"),
            "departure_date": row.get("departure_date"),
            "adults": row.get("adults") or 0,
            "children": row.get("children") or 0,
        },
        "transport": {
            "transfer": "Airport drop-off",
            "eta": _text(row.get("transport_time") or row.get("departure_time")),
            "flight": _text(row.get("transport_flight")),
            "pickup_location": "",
            "destination": _airport_label(row, "destination"),
            "source_type": _text(row.get("transport_type")),
        },
    }


def load_transportation_guests(client_code: str) -> list[dict[str, Any]]:
    """Load the operational views and assignments for the active property.

    The transportation views are already scoped to the available property data
    and do not expose a ``client_code`` column, so they must not be filtered by
    client at the REST layer. Saved dispatch assignments remain isolated by the
    active GCP client code.
    """
    client = get_reports_supabase()
    arrivals = (
        client.table(ARRIVALS_VIEW)
        .select("*")
        .execute()
    )
    departures = (
        client.table(DEPARTURES_VIEW)
        .select("*")
        .execute()
    )

    guests = [_map_arrival(dict(row)) for row in (arrivals.data or [])]
    guests.extend(_map_departure(dict(row)) for row in (departures.data or []))

    assignments = (
        get_supabase()
        .table(ASSIGNMENTS_TABLE)
        .select("*")
        .eq("client_code", client_code)
        .execute()
    )
    assignments_by_key = {
        _text(row.get("record_key")): dict(row)
        for row in (assignments.data or [])
    }
    for guest in guests:
        assignment = assignments_by_key.get(_text(guest.get("id")))
        if assignment:
            guest["transport_assignment"] = assignment

    return guests


def save_transportation_assignment(
    client_code: str,
    guest: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    direction = "Arrival" if guest.get("movement") == "Arrivals" else "Departure"
    stay = guest.get("stay", {}) or {}
    movement_date = stay.get("arrival_date" if direction == "Arrival" else "departure_date")
    record = {
        "record_key": _text(guest.get("id")),
        "client_code": client_code,
        "direction": direction,
        "movement_date": movement_date,
        "guest_name": _text(guest.get("full_name")),
        **payload,
    }
    response = (
        get_supabase()
        .table(ASSIGNMENTS_TABLE)
        .upsert(record, on_conflict="record_key")
        .execute()
    )
    return dict(response.data[0]) if response.data else record
