from __future__ import annotations

from pathlib import Path
from typing import Any


def send_guest_email(guest: dict[str, Any]) -> bool:
    """Demo placeholder for Microsoft Graph or another email provider."""
    return bool(guest.get("email"))


def send_bulk_emails(
    guests: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Send one email per reservation.

    The workspace passes only reservations with:
    - an email address
    - a generated DOCX
    - a generated PDF
    """
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
                results.append(
                    {
                        "guest_id": guest_id,
                        "Guest": full_name,
                        "Email": email,
                        "Status": "Sent",
                        "Message": "Email sent successfully",
                    }
                )
            else:
                failed += 1
                results.append(
                    {
                        "guest_id": guest_id,
                        "Guest": full_name,
                        "Email": email,
                        "Status": "Failed",
                        "Message": "Email provider returned False",
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
