from __future__ import annotations

import base64
import json
import secrets
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from core.config import load_client_config

BASE_DIR = Path(__file__).resolve().parents[1]
_WRITE_LOCK = threading.Lock()


def _client_code() -> str:
    config = load_client_config()
    return str(config.get("client", {}).get("code", "default"))


def _store_path() -> Path:
    config = load_client_config()
    client = config.get("client", {})
    folder = str(client.get("data_folder") or client.get("code") or "default")
    path = BASE_DIR / "data" / folder / "registration_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _empty_store() -> dict[str, Any]:
    return {
        "sequences": {},
        "cards": [],
    }


def _read_store() -> dict[str, Any]:
    path = _store_path()
    if not path.exists():
        return _empty_store()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_store()

    data.setdefault("sequences", {})
    data.setdefault("cards", [])
    return data


def _write_store(data: dict[str, Any]) -> None:
    path = _store_path()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary.replace(path)


def list_registration_cards() -> list[dict[str, Any]]:
    cards = _read_store()["cards"]
    return sorted(
        cards,
        key=lambda card: card.get("created_at", ""),
        reverse=True,
    )


def get_card_by_guest_id(guest_id: str) -> dict[str, Any] | None:
    return next(
        (
            card
            for card in _read_store()["cards"]
            if card.get("guest_id") == guest_id
        ),
        None,
    )


def get_card_by_token(token: str) -> dict[str, Any] | None:
    return next(
        (
            card
            for card in _read_store()["cards"]
            if secrets.compare_digest(str(card.get("token", "")), str(token))
        ),
        None,
    )


def _next_correlative(data: dict[str, Any], year: int) -> str:
    sequence_key = str(year)
    current = int(data["sequences"].get(sequence_key, 0)) + 1
    data["sequences"][sequence_key] = current
    return f"RC-{year}-{current:06d}"


def _guest_snapshot(guest: dict[str, Any]) -> dict[str, Any]:
    stay = guest.get("stay", {})
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


def create_or_get_registration_card(
    guest: dict[str, Any],
    base_url: str | None = None,
) -> dict[str, Any]:
    guest_id = str(guest["id"])

    with _WRITE_LOCK:
        data = _read_store()

        existing = next(
            (
                card
                for card in data["cards"]
                if card.get("guest_id") == guest_id
            ),
            None,
        )
        if existing:
            return existing

        config = load_client_config()
        registration_config = config.get("registration_cards", {})
        year = datetime.now().year
        correlative = _next_correlative(data, year)
        token = secrets.token_urlsafe(24)

        configured_url = str(
            base_url
            or registration_config.get("public_base_url")
            or "http://localhost:8501"
        ).rstrip("/")
        public_url = f"{configured_url}/?registration_token={token}"

        now = datetime.now().isoformat(timespec="seconds")
        card = {
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

        data["cards"].append(card)
        _write_store(data)
        return card


def update_card_status(
    registration_card_number: str,
    status: str,
    **values: Any,
) -> dict[str, Any]:
    with _WRITE_LOCK:
        data = _read_store()

        for card in data["cards"]:
            if card.get("registration_card_number") == registration_card_number:
                card["status"] = status
                card.update(values)
                _write_store(data)
                return card

    raise KeyError(
        f"Registration card not found: {registration_card_number}"
    )


def mark_card_sent(registration_card_number: str) -> dict[str, Any]:
    return update_card_status(
        registration_card_number,
        "Sent",
        sent_at=datetime.now().isoformat(timespec="seconds"),
    )


def mark_card_opened(token: str) -> dict[str, Any] | None:
    with _WRITE_LOCK:
        data = _read_store()

        for card in data["cards"]:
            if secrets.compare_digest(str(card.get("token", "")), str(token)):
                if not card.get("opened_at"):
                    card["opened_at"] = datetime.now().isoformat(
                        timespec="seconds"
                    )
                if card.get("status") in {"Generated", "Sent"}:
                    card["status"] = "Opened"
                _write_store(data)
                return card

    return None


def save_guest_response(
    token: str,
    response: dict[str, Any],
    signature_png: bytes,
) -> dict[str, Any]:
    signature_base64 = base64.b64encode(signature_png).decode("ascii")
    completed_at = datetime.now().isoformat(timespec="seconds")

    with _WRITE_LOCK:
        data = _read_store()

        for card in data["cards"]:
            if secrets.compare_digest(str(card.get("token", "")), str(token)):
                card["status"] = "Signed"
                card["completed_at"] = completed_at
                card["response"] = {
                    **response,
                    "signature_png_base64": signature_base64,
                    "signed_at": completed_at,
                }
                _write_store(data)
                return card

    raise KeyError("The registration-card link is invalid or expired.")
