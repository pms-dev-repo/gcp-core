from __future__ import annotations

from typing import Any

from services.registration_card_service import mark_card_sent


def send_guest_email(guest: dict[str, Any]) -> bool:
    """Demo placeholder for Microsoft Graph or another email provider."""
    return bool(guest.get("email"))


def send_registration_card_email(
    guest: dict[str, Any],
    card: dict[str, Any],
) -> bool:
    """
    Demo delivery.

    In production this function can be replaced with Microsoft Graph.
    The generated public URL is already available in card["public_url"].
    """
    if not guest.get("email"):
        return False

    mark_card_sent(card["registration_card_number"])
    return True


def send_bulk_emails(
    guests: list[dict[str, Any]],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    sent = 0
    failed = 0
    skipped = 0

    for guest in guests:
        guest_id = guest["id"]
        full_name = guest.get("full_name") or "Unknown guest"
        email = guest.get("email")

        if not email:
            skipped += 1
            results.append(
                {
                    "guest_id": guest_id,
                    "Guest": full_name,
                    "Email": "—",
                    "Status": "Skipped",
                    "Message": "Missing email",
                }
            )
            continue

        try:
            success = send_guest_email(guest)
            if success:
                sent += 1
                status = "Sent"
                message = "Email sent successfully"
            else:
                failed += 1
                status = "Failed"
                message = "Email provider returned False"

            results.append(
                {
                    "guest_id": guest_id,
                    "Guest": full_name,
                    "Email": email,
                    "Status": status,
                    "Message": message,
                }
            )
        except Exception as exc:
            failed += 1
            results.append(
                {
                    "guest_id": guest_id,
                    "Guest": full_name,
                    "Email": email,
                    "Status": "Failed",
                    "Message": str(exc),
                }
            )

    return {
        "total": len(guests),
        "sent": sent,
        "failed": failed,
        "skipped": skipped,
        "results": results,
    }
