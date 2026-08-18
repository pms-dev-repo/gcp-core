from __future__ import annotations

from typing import Any

from services.database import get_reports_supabase


REPEAT_GUEST_MONTHLY_VIEW = "rpt_repeat_guest_monthly"
DAILY_FIGURES_VIEW = "vw_daily_figures"
STATISTICS_MANAGER_TABLE = "rpt_statistics_manager"
ROOM_PERFORMANCE_VIEW = "rpt_room_performance"
GUEST_FOLIO_DETAILS_TABLE = "rpt_guest_folio_details"
GUEST_FOLIO_SUMMARY_VIEW = "rpt_guest_folio_summary"
STATISTICS_MANAGER_COLUMNS = [
    "business_date",
    "property",
    "arrival_rooms",
    "departure_rooms",
    "individual_rooms",
    "group_rooms",
    "no_show_rooms",
    "cancel_rooms",
    "walk_in_rooms",
    "house_use_rooms",
    "day_use_rooms",
    "complimentary_rooms",
    "extended_stay_rooms",
    "occupancy_pct",
    "occupancy_pct_minus_complimentary_house_use",
    "occupancy_pct_minus_complimentary_house_use_out_of_order",
    "occupied_rooms",
    "out_of_order_rooms",
    "room_revenue",
    "fb_revenue",
    "other_revenue",
    "total_revenue",
    "room_tax",
    "fb_tax",
    "other_tax",
    "total_tax",
]


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
        get_reports_supabase()
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
        get_reports_supabase()
        .table(REPEAT_GUEST_MONTHLY_VIEW)
        .select("*")
        .eq("property", property_code)
        .in_("calendar_year", years)
        .order("stay_month")
        .execute()
    )
    return [dict(row) for row in (response.data or [])]


def load_daily_figures() -> list[dict[str, Any]]:
    """Load Daily Figures in the display order defined by the source view."""
    response = (
        get_reports_supabase()
        .table(DAILY_FIGURES_VIEW)
        .select("*")
        .order("business_date", desc=True)
        .order("sort_order")
        .execute()
    )
    return [dict(row) for row in (response.data or [])]


def load_statistics_manager(property_code: str) -> list[dict[str, Any]]:
    """Load Statistics Manager rows for the active property."""
    response = (
        get_reports_supabase()
        .table(STATISTICS_MANAGER_TABLE)
        .select(",".join(STATISTICS_MANAGER_COLUMNS))
        .eq("property", property_code)
        .order("business_date", desc=True)
        .execute()
    )
    return [dict(row) for row in (response.data or [])]


def load_room_performance(property_code: str) -> list[dict[str, Any]]:
    """Load the room-night ranking for the active property."""
    response = (
        get_reports_supabase()
        .table(ROOM_PERFORMANCE_VIEW)
        .select("*")
        .eq("property", property_code)
        .order("room_nights", desc=True)
        .order("stay_count", desc=True)
        .execute()
    )
    return [dict(row) for row in (response.data or [])]


def load_guest_folio_summaries(
    property_code: str,
    search_term: str = "",
    checkout_date: str | None = None,
) -> list[dict[str, Any]]:
    """Find guest folios by guest name, room, bill number, or checkout date."""
    normalized_search = search_term.strip().replace(",", " ")
    if not normalized_search and not checkout_date:
        return []

    query = (
        get_reports_supabase()
        .table(GUEST_FOLIO_SUMMARY_VIEW)
        .select("*")
        .eq("property", property_code)
    )
    if checkout_date:
        query = query.eq("bill_generation_date", checkout_date)
    if normalized_search:
        query = query.or_(
            "display_name.ilike.%{term}%,room.ilike.%{term}%,bill_no.ilike.%{term}%".format(
                term=normalized_search
            )
        )
    response = query.order("bill_generation_date", desc=True).limit(100).execute()
    return [dict(row) for row in (response.data or [])]


def load_guest_folio_transactions(
    property_code: str,
    bill_no: str,
) -> list[dict[str, Any]]:
    """Load the transaction rows that make up one selected folio."""
    response = (
        get_reports_supabase()
        .table(GUEST_FOLIO_DETAILS_TABLE)
        .select(
            "trx_no,trx_code,trx_date,ft_debit,ft_credit,transaction_description"
        )
        .eq("property", property_code)
        .eq("bill_no", bill_no)
        .order("trx_date")
        .order("folio_detail_id")
        .execute()
    )
    return [dict(row) for row in (response.data or [])]
