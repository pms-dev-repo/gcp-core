from __future__ import annotations

import base64
import secrets
from datetime import datetime, timezone
from typing import Any

from core.config import load_client_config
from services.database import get_supabase

TABLE_NAME = "registration_cards"


class RegistrationCardError(RuntimeError):
    """Raised when a registration-card database operation fails."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _client_code() -> str:
    config = load_client_config()
    return str(config.get("client", {}).get("code", "default"))


def _first_row(result: Any) -> dict[str, Any] | None:
    rows = getattr(result, "data", None) or []
    return dict(rows[0]) if rows else None


def _guest_snapshot(guest: dict[str, Any]) -> dict[str, Any]:
    stay = guest.get("stay", {}) or {}
    return {
        "guest_id": guest.get("id"),
        "confirmation_number": guest.get("confirmation_number"),
        "reservation_name_id": guest.get("reservation_name_id"),
        "salutation": guest.get("salutation"),
        "first_name": guest.get("first_name"),
        "last_name": guest.get("last_name"),
        "full_name": guest.get("full_name"),
        "email": guest.get("email"),
        "phone": guest.get("phone"),
        "nationality": guest.get("nationality"),
        "document_type": guest.get("document_type"),
        "document_number": guest.get("document_number"),
        "room": guest.get("room"),
        "room_type": guest.get("room_type"),
        "rate_code": guest.get("rate_code"),
        "company": guest.get("company"),
        "arrival_date": stay.get("arrival_date"),
        "departure_date": stay.get("departure_date"),
        "nights": stay.get("nights"),
        "adults": stay.get("adults"),
        "children": stay.get("children"),
    }


def list_registration_cards() -> list[dict[str, Any]]:
    """Return all registration cards for the active client, newest first."""
    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .select("*")
            .eq("client_code", _client_code())
            .order("created_at", desc=True)
            .execute()
        )
        return [dict(row) for row in (result.data or [])]
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to list registration cards: {exc}"
        ) from exc


def get_card_by_guest_id(guest_id: str) -> dict[str, Any] | None:
    """Find the current client's card for a guest."""
    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .select("*")
            .eq("client_code", _client_code())
            .eq("guest_id", str(guest_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return _first_row(result)
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to find registration card for guest {guest_id}: {exc}"
        ) from exc


def get_card_by_token(token: str) -> dict[str, Any] | None:
    """Find a card by its public token."""
    token = str(token or "").strip()
    if not token:
        return None

    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .select("*")
            .eq("token", token)
            .limit(1)
            .execute()
        )
        return _first_row(result)
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to find registration card by token: {exc}"
        ) from exc


def _next_correlative(client_code: str, year: int) -> str:
    """Return the next RC-YYYY-###### number for the active client."""
    prefix = f"RC-{year}-"

    result = (
        get_supabase()
        .table(TABLE_NAME)
        .select("registration_card_number")
        .eq("client_code", client_code)
        .like("registration_card_number", f"{prefix}%")
        .order("registration_card_number", desc=True)
        .limit(1)
        .execute()
    )

    last_row = _first_row(result)
    if not last_row:
        return f"{prefix}000001"

    last_number = str(last_row.get("registration_card_number", ""))
    try:
        sequence = int(last_number.rsplit("-", 1)[-1]) + 1
    except (TypeError, ValueError):
        sequence = 1

    return f"{prefix}{sequence:06d}"


def create_or_get_registration_card(
    guest: dict[str, Any],
    base_url: str | None = None,
) -> dict[str, Any]:
    """Return an existing card for the guest or create one in Supabase."""
    if "id" not in guest:
        raise ValueError("Guest data is missing the required 'id' field.")

    guest_id = str(guest["id"])
    existing = get_card_by_guest_id(guest_id)
    if existing:
        return existing

    config = load_client_config()
    registration_config = config.get("registration_cards", {}) or {}
    client_code = str(config.get("client", {}).get("code", "default"))
    year = datetime.now(timezone.utc).year

    configured_url = str(
        base_url
        or registration_config.get("public_base_url")
        or "http://localhost:8501"
    ).rstrip("/")

    supabase = get_supabase()

    # Retry protects against the uncommon case where two requests calculate
    # the same correlative at almost the same time.
    for _ in range(3):
        correlative = _next_correlative(client_code, year)
        token = secrets.token_urlsafe(24)
        public_url = (
            f"{configured_url}/?client={client_code}"
            f"&registration_token={token}"
        )
        now = _now_iso()

        payload = {
            "client_code": client_code,
            "registration_card_number": correlative,
            "guest_id": guest_id,
            "confirmation_number": guest.get("confirmation_number"),
            "token": token,
            "public_url": public_url,
            "status": "Generated",
            "created_at": now,
            "generated_at": now,
            "sent_at": None,
            "opened_at": None,
            "completed_at": None,
            "guest": _guest_snapshot(guest),
            "response": {},
        }

        try:
            result = supabase.table(TABLE_NAME).insert(payload).execute()
            created = _first_row(result)
            if created:
                return created
            raise RegistrationCardError(
                "Supabase did not return the newly created registration card."
            )
        except Exception as exc:
            # Another request may have created the guest's card first.
            existing = get_card_by_guest_id(guest_id)
            if existing:
                return existing

            error_text = str(exc).lower()
            duplicate_error = (
                "duplicate" in error_text
                or "unique" in error_text
                or "23505" in error_text
            )
            if not duplicate_error:
                raise RegistrationCardError(
                    f"Unable to create registration card: {exc}"
                ) from exc

    raise RegistrationCardError(
        "Unable to generate a unique registration-card number after 3 attempts."
    )


def update_card_status(
    registration_card_number: str,
    status: str,
    **values: Any,
) -> dict[str, Any]:
    """Update a card belonging to the active client and return it."""
    payload = {"status": status, **values}

    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .update(payload)
            .eq("client_code", _client_code())
            .eq("registration_card_number", registration_card_number)
            .execute()
        )
        updated = _first_row(result)
        if updated:
            return updated
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to update registration card {registration_card_number}: {exc}"
        ) from exc

    raise KeyError(f"Registration card not found: {registration_card_number}")


def mark_card_sent(registration_card_number: str) -> dict[str, Any]:
    return update_card_status(
        registration_card_number,
        "Sent",
        sent_at=_now_iso(),
    )


def mark_card_opened(token: str) -> dict[str, Any] | None:
    card = get_card_by_token(token)
    if not card:
        return None

    values: dict[str, Any] = {}
    if not card.get("opened_at"):
        values["opened_at"] = _now_iso()

    status = str(card.get("status") or "")
    new_status = "Opened" if status in {"Generated", "Sent"} else status

    if not values and new_status == status:
        return card

    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .update({"status": new_status, **values})
            .eq("token", str(token))
            .execute()
        )
        return _first_row(result) or card
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to mark registration card as opened: {exc}"
        ) from exc


def save_guest_response(
    token: str,
    response: dict[str, Any],
    signature_png: bytes,
) -> dict[str, Any]:
    card = get_card_by_token(token)
    if not card:
        raise KeyError("The registration-card link is invalid or expired.")

    signature_base64 = base64.b64encode(signature_png).decode("ascii")
    completed_at = _now_iso()
    response_payload = {
        **response,
        "signature_png_base64": signature_base64,
        "signed_at": completed_at,
    }

    try:
        result = (
            get_supabase()
            .table(TABLE_NAME)
            .update(
                {
                    "status": "Signed",
                    "completed_at": completed_at,
                    "response": response_payload,
                }
            )
            .eq("token", str(token))
            .execute()
        )
        updated = _first_row(result)
        if updated:
            return updated
    except Exception as exc:
        raise RegistrationCardError(
            f"Unable to save the guest response: {exc}"
        ) from exc

    raise KeyError("The registration-card link is invalid or expired.")
