from __future__ import annotations

from typing import Any

from services.database import get_supabase


REPEAT_GUEST_MONTHLY_VIEW = "rpt_repeat_guest_monthly"


def report_property_code(client_code: str, config: dict[str, Any]) -> str:
    """Return the reporting property code configured for a GCP client."""
    reports = config.get("reports") or {}
    return str(reports.get("property_code") or client_code).strip()


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def available_report_years(property_code: str) -> list[int]:
    """Return the years available in the monthly reporting view."""
    response = (
        get_supabase()
        .table(REPEAT_GUEST_MONTHLY_VIEW)
        .select("calendar_year")
        .eq("property", property_code)
        .execute()
    )
    years = {
        year
        for row in (response.data or [])
        if (year := _as_int(dict(row).get("calendar_year"))) is not None
    }
    return sorted(years, reverse=True)


def load_repeat_guest_monthly(
    property_code: str,
    years: list[int],
) -> list[dict[str, Any]]:
    """Load monthly repeat-guest measures for the selected property and years."""
    if not years:
        return []

    response = (
        get_supabase()
        .table(REPEAT_GUEST_MONTHLY_VIEW)
        .select("*")
        .eq("property", property_code)
        .in_("calendar_year", years)
        .order("stay_month")
        .execute()
    )
    return [dict(row) for row in (response.data or [])]
