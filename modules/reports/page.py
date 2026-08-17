from __future__ import annotations

from calendar import month_abbr
from datetime import date
from io import BytesIO
from typing import Any
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.config import get_active_client_code, load_client_config
from modules.reports.service import (
    available_report_years,
    load_daily_figures,
    load_repeat_guest_monthly,
    load_statistics_manager,
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


def _pdf_cell_value(column: str, value: Any) -> str:
    if column == "Month":
        return str(value)
    if "%" in column:
        return f"{float(value):.1%}"
    return f"{int(value):,}"


def _pdf_table(title: str, frame: pd.DataFrame) -> list[Any]:
    table_data = [list(frame.columns)]
    table_data.extend(
        [
            [_pdf_cell_value(column, row[column]) for column in frame.columns]
            for _, row in frame.iterrows()
        ]
    )
    column_widths = [21 * mm] + [20.5 * mm] * (len(frame.columns) - 1)
    table = Table(table_data, colWidths=column_widths, repeatRows=1)
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12213f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
    for row_index, (_, row) in enumerate(frame.iterrows(), start=1):
        for column_index, column in enumerate(frame.columns[1:], start=1):
            try:
                if float(row[column]) < 0:
                    table_style.add(
                        "TEXTCOLOR", (column_index, row_index), (column_index, row_index), colors.HexColor("#c62828")
                    )
            except (TypeError, ValueError):
                continue
    table.setStyle(table_style)

    styles = getSampleStyleSheet()
    return [
        Paragraph(title, styles["Heading3"]),
        Spacer(1, 2 * mm),
        table,
        Spacer(1, 6 * mm),
    ]


def build_repeat_guest_report_pdf(
    property_name: str,
    report_year: int,
    comparison_year: int,
    start_month: int,
    end_month: int,
    guest_table: pd.DataFrame,
    night_table: pd.DataFrame,
) -> bytes:
    """Build a download-ready PDF matching the visible report filters."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=8 * mm,
        rightMargin=8 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="Repeat Guest Report",
    )
    styles = getSampleStyleSheet()
    month_range = f"{month_abbr[start_month]} - {month_abbr[end_month]}"
    story: list[Any] = [
        Paragraph("Repeat Guest Report", styles["Title"]),
        Paragraph(escape(property_name), styles["Heading3"]),
        Paragraph(
            f"Period: {month_range} {report_year} | Comparison: {comparison_year}",
            styles["BodyText"],
        ),
        Paragraph(f"Generated: {date.today():%d %b %Y}", styles["BodyText"]),
        Spacer(1, 5 * mm),
    ]
    story.extend(_pdf_table("Repeat Guests", guest_table))
    story.extend(_pdf_table("Repeat Nights", night_table))
    document.build(story)
    return buffer.getvalue()


def _render_table(title: str, frame: pd.DataFrame) -> None:
    st.subheader(title)
    percentage_columns = [column for column in frame.columns if "%" in column]
    numeric_columns = [column for column in frame.columns if column != "Month"]
    styled_frame = frame.style.format(
        {column: "{:.1%}" for column in percentage_columns}
    ).map(_negative_value_style, subset=numeric_columns)
    st.dataframe(
        styled_frame,
        use_container_width=True,
        hide_index=True,
    )


def _render_daily_figures() -> None:
    try:
        rows = load_daily_figures()
    except DatabaseConfigurationError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("The Daily Figures data could not be loaded. Please try again.")
        return

    if not rows:
        st.info("No Daily Figures data is available yet.")
        return

    st.subheader("Daily Figures")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_statistics_manager(property_code: str) -> None:
    try:
        rows = load_statistics_manager(property_code)
    except DatabaseConfigurationError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("The Statistics Manager data could not be loaded. Please try again.")
        return

    if not rows:
        st.info("No Statistics Manager data is available yet.")
        return

    st.subheader("Statistics Manager")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _open_report(report_name: str) -> None:
    st.session_state.reports_selected_report = report_name


def _render_report_catalog() -> None:
    st.subheader("Available reports")
    repeat_column, daily_column, statistics_column = st.columns(3, gap="large")

    with repeat_column:
        with st.container(border=True):
            st.markdown("### Repeat Guest Report")
            st.caption("New and Repeat guests, room nights, and year-over-year variance.")
            st.button(
                "Open Repeat Guest Report",
                key="open_repeat_guest_report",
                use_container_width=True,
                on_click=_open_report,
                args=("Repeat Guest Report",),
            )

    with daily_column:
        with st.container(border=True):
            st.markdown("### Daily Figures")
            st.caption("Daily in-house, departures, arrivals, expected in-house, and EXO.")
            st.button(
                "Open Daily Figures",
                key="open_daily_figures",
                use_container_width=True,
                on_click=_open_report,
                args=("Daily Figures",),
            )

    with statistics_column:
        with st.container(border=True):
            st.markdown("### Statistics Manager")
            st.caption("Daily occupancy, room movement, revenue, and tax statistics.")
            st.button(
                "Open Statistics Manager",
                key="open_statistics_manager",
                use_container_width=True,
                on_click=_open_report,
                args=("Statistics Manager",),
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

    selected_report = st.session_state.get("reports_selected_report")
    if not selected_report:
        _render_report_catalog()
        return

    if st.button("← All reports", key="reports_back_to_catalog"):
        st.session_state.pop("reports_selected_report", None)
        st.rerun()

    if selected_report == "Daily Figures":
        _render_daily_figures()
        return
    if selected_report == "Statistics Manager":
        _render_statistics_manager(property_code)
        return

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
    pdf_bytes = build_repeat_guest_report_pdf(
        property_name,
        report_year,
        comparison_year,
        start_month,
        end_month,
        guest_table,
        night_table,
    )
    st.download_button(
        "Download report as PDF",
        data=pdf_bytes,
        file_name=f"repeat_guest_report_{property_code}_{report_year}.pdf",
        mime="application/pdf",
        key="reports_download_pdf",
    )
    _render_table("Repeat Guest Report", guest_table)
    _render_table("Repeat Nights Report", night_table)
