from __future__ import annotations

from calendar import month_abbr
from typing import Any

import pandas as pd
import streamlit as st

from core.config import get_active_client_code, load_client_config
from modules.reports.service import (
    available_report_years,
    load_repeat_guest_monthly,
    report_property_code,
)
from services.database import DatabaseConfigurationError


def _number(row: dict[str, Any] | None, key: str) -> int:
    if not row:
        return 0
    try:
        return int(row.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _month_rows(
    rows: list[dict[str, Any]],
    year: int,
) -> dict[int, dict[str, Any]]:
    return {
        int(row["calendar_month"]): row
        for row in rows
        if int(row.get("calendar_year") or 0) == year
    }


def _comparison_table(
    rows: list[dict[str, Any]],
    report_year: int,
    comparison_year: int,
    start_month: int,
    end_month: int,
    measure: str,
) -> pd.DataFrame:
    current = _month_rows(rows, report_year)
    comparison = _month_rows(rows, comparison_year)
    is_guest_measure = measure == "guests"
    repeat_key = "repeat_guests" if is_guest_measure else "repeat_nights"
    new_key = "new_guests" if is_guest_measure else "new_nights"

    rendered: list[dict[str, Any]] = []
    for month in range(start_month, end_month + 1):
        current_row = current.get(month)
        comparison_row = comparison.get(month)
        current_repeat = _number(current_row, repeat_key)
        current_new = _number(current_row, new_key)
        comparison_repeat = _number(comparison_row, repeat_key)
        comparison_new = _number(comparison_row, new_key)
        current_total = current_repeat + current_new
        comparison_total = comparison_repeat + comparison_new
        current_repeat_pct = _ratio(current_repeat, current_total)
        comparison_repeat_pct = _ratio(comparison_repeat, comparison_total)
        current_new_pct = _ratio(current_new, current_total)
        comparison_new_pct = _ratio(comparison_new, comparison_total)

        rendered.append(
            {
                "Month": month_abbr[month],
                f"{report_year} Repeat": current_repeat,
                "% Repeat": current_repeat_pct,
                f"{comparison_year} Repeat": comparison_repeat,
                "% Repeat prior": comparison_repeat_pct,
                "YOY Repeat": current_repeat - comparison_repeat,
                "YOY Repeat %": current_repeat_pct - comparison_repeat_pct,
                f"{report_year} New": current_new,
                "% New": current_new_pct,
                f"{comparison_year} New": comparison_new,
                "% New prior": comparison_new_pct,
                "YOY New": current_new - comparison_new,
                "YOY New %": current_new_pct - comparison_new_pct,
            }
        )

    frame = pd.DataFrame(rendered)
    totals = {
        "Month": "Total / Avg",
        f"{report_year} Repeat": int(frame[f"{report_year} Repeat"].sum()),
        f"{comparison_year} Repeat": int(frame[f"{comparison_year} Repeat"].sum()),
        f"{report_year} New": int(frame[f"{report_year} New"].sum()),
        f"{comparison_year} New": int(frame[f"{comparison_year} New"].sum()),
    }
    current_total = totals[f"{report_year} Repeat"] + totals[f"{report_year} New"]
    comparison_total = totals[f"{comparison_year} Repeat"] + totals[f"{comparison_year} New"]
    totals["% Repeat"] = _ratio(totals[f"{report_year} Repeat"], current_total)
    totals["% Repeat prior"] = _ratio(totals[f"{comparison_year} Repeat"], comparison_total)
    totals["YOY Repeat"] = totals[f"{report_year} Repeat"] - totals[f"{comparison_year} Repeat"]
    totals["YOY Repeat %"] = totals["% Repeat"] - totals["% Repeat prior"]
    totals["% New"] = _ratio(totals[f"{report_year} New"], current_total)
    totals["% New prior"] = _ratio(totals[f"{comparison_year} New"], comparison_total)
    totals["YOY New"] = totals[f"{report_year} New"] - totals[f"{comparison_year} New"]
    totals["YOY New %"] = totals["% New"] - totals["% New prior"]
    return pd.concat([frame, pd.DataFrame([totals])], ignore_index=True)


def _negative_value_style(value: Any) -> str:
    """Highlight negative report measures without changing their displayed value."""
    try:
        return "color: #c62828; font-weight: 600;" if float(value) < 0 else ""
    except (TypeError, ValueError):
        return ""


def _render_table(title: str, frame: pd.DataFrame) -> None:
    st.subheader(title)
    percentage_columns = [column for column in frame.columns if "%" in column]
    numeric_columns = [column for column in frame.columns if column != "Month"]
    styled_frame = frame.style.format(
        {column: "{:.1%}" for column in percentage_columns}
    ).applymap(_negative_value_style, subset=numeric_columns)
    st.dataframe(
        styled_frame,
        use_container_width=True,
        hide_index=True,
    )


def render(*_args, **_kwargs) -> None:
    client_code = get_active_client_code()
    config = load_client_config(client_code)
    property_code = report_property_code(client_code, config)
    property_name = str((config.get("client") or {}).get("name") or property_code)

    st.markdown(
        f"""
        <section class="dashboard-hero">
            <div>
                <div class="dashboard-eyebrow">PROPERTY ANALYTICS</div>
                <h1>▤ Reports</h1>
                <p>Repeat guest performance sourced from OPERA Reporting &amp; Analytics.</p>
            </div>
            <div class="dashboard-property-chip">● {property_name}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    try:
        years = available_report_years(property_code)
    except DatabaseConfigurationError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("The reporting data could not be loaded. Please try again.")
        return

    if not years:
        st.info(f"No reporting data is available yet for property {property_code}.")
        return

    report_year = st.selectbox("Report year", years, key="reports_year")
    comparison_year = report_year - 1
    if comparison_year not in years:
        alternatives = [year for year in years if year != report_year]
        if not alternatives:
            st.info("A second year of data is required to calculate year-over-year variation.")
            return
        comparison_year = st.selectbox(
            "Comparison year",
            alternatives,
            key="reports_comparison_year",
        )

    try:
        rows = load_repeat_guest_monthly(property_code, [report_year, comparison_year])
    except Exception:
        st.error("The reporting data could not be loaded. Please try again.")
        return

    available_months = [
        int(row["calendar_month"])
        for row in rows
        if int(row.get("calendar_year") or 0) == report_year
    ]
    default_end_month = max(available_months, default=12)
    start_month, end_month = st.select_slider(
        "Reporting months",
        options=list(range(1, 13)),
        value=(1, default_end_month),
        format_func=lambda month: month_abbr[month],
        key="reports_month_range",
    )

    guest_table = _comparison_table(
        rows, report_year, comparison_year, start_month, end_month, "guests"
    )
    night_table = _comparison_table(
        rows, report_year, comparison_year, start_month, end_month, "nights"
    )

    st.caption(
        "Repeat and New classification is based on the guest's stay history at the property. "
        "Room nights are assigned to the arrival month."
    )
    _render_table("Repeat Guest Report", guest_table)
    _render_table("Repeat Nights Report", night_table)
