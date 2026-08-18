from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from modules.reports.service import (
    load_guest_folio_summaries,
    load_guest_folio_transactions,
)
from services.database import DatabaseConfigurationError


GCP_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "gcp_logo.png"


def _as_amount(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _format_amount(value: Any) -> str:
    return f"${_as_amount(value):,.2f}"


def _folio_label(folio: dict[str, Any]) -> str:
    guest = str(folio.get("display_name") or "Unknown guest")
    room = str(folio.get("room") or "No room")
    bill = str(folio.get("bill_no") or "-")
    bill_date = str(folio.get("bill_generation_date") or "")
    return f"{guest} | Room {room} | Folio {bill} | {bill_date}"


def _simulated_email(bill_no: str) -> str:
    """Return a deterministic, clearly fictitious recipient per folio."""
    return f"folio-{bill_no}@example.com"


def build_guest_folio_pdf(
    property_name: str,
    folio: dict[str, Any],
    transactions: list[dict[str, Any]],
) -> bytes:
    """Build a guest-ready PDF for one selected folio."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"Guest Folio {folio.get('bill_no')}",
    )
    styles = getSampleStyleSheet()
    total_debit = sum(_as_amount(row.get("ft_debit")) for row in transactions)
    total_credit = sum(_as_amount(row.get("ft_credit")) for row in transactions)
    balance = total_debit - total_credit
    details = [
        ["Guest", str(folio.get("display_name") or "-")],
        ["Room", str(folio.get("room") or "-")],
        ["Folio", str(folio.get("bill_no") or "-")],
        ["Folio date", str(folio.get("bill_generation_date") or "-")],
        ["Status", str(folio.get("status") or "-")],
    ]
    detail_table = Table(details, colWidths=[32 * mm, 136 * mm])
    detail_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    transaction_data = [["Date", "Code", "Description", "Debit", "Credit"]]
    for transaction in transactions:
        transaction_data.append(
            [
                str(transaction.get("trx_date") or "-"),
                str(transaction.get("trx_code") or "-"),
                Paragraph(
                    escape(str(transaction.get("transaction_description") or "-")),
                    styles["BodyText"],
                ),
                _format_amount(transaction.get("ft_debit")),
                _format_amount(transaction.get("ft_credit")),
            ]
        )
    transaction_data.append(
        ["", "", "Total", _format_amount(total_debit), _format_amount(total_credit)]
    )
    transaction_data.append(["", "", "Balance", "", _format_amount(balance)])
    transaction_table = Table(
        transaction_data,
        colWidths=[27 * mm, 19 * mm, 75 * mm, 30 * mm, 30 * mm],
        repeatRows=1,
    )
    transaction_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12213f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -2), (-1, -1), colors.HexColor("#f1f5f9")),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -3), [colors.white, colors.HexColor("#f8fafc")]),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    logo = Image(str(GCP_LOGO_PATH), width=45 * mm, height=12 * mm)
    header = Table(
        [[logo, Paragraph("Guest Folio", styles["Title"])]],
        colWidths=[52 * mm, 116 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story: list[Any] = [
        header,
        Spacer(1, 3 * mm),
        Paragraph(escape(property_name), styles["Heading3"]),
        Paragraph(f"Generated: {date.today():%d %b %Y}", styles["BodyText"]),
        Spacer(1, 5 * mm),
        detail_table,
        Spacer(1, 7 * mm),
        Paragraph("Transaction details", styles["Heading3"]),
        Spacer(1, 2 * mm),
        transaction_table,
    ]
    document.build(story)
    return buffer.getvalue()


def render_guest_folios(property_code: str, property_name: str) -> None:
    st.subheader("Guest Folios")
    st.caption("Search by guest name, room, folio number, or checkout date. Email delivery is a simulation only and does not send an email.")
    checkout_date = st.date_input(
        "Checkout date",
        value=None,
        help="Uses the folio generation date supplied by OPERA R&A.",
        key="guest_folios_checkout_date",
    )
    search_term = st.text_input(
        "Guest, room, or folio number",
        key="guest_folios_search",
        placeholder="For example: Smith, 317, or 196992",
    ).strip()
    if not search_term and not checkout_date:
        st.info("Enter a guest name, room, folio number, or select a checkout date to find a folio.")
        return

    try:
        folios = load_guest_folio_summaries(
            property_code,
            search_term,
            checkout_date.isoformat() if checkout_date else None,
        )
    except DatabaseConfigurationError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("The guest folios could not be loaded. Please try again.")
        return

    if not folios:
        st.info("No folios matched that search.")
        return

    selected_label = st.selectbox(
        "Select a folio",
        options=[_folio_label(folio) for folio in folios],
        key="guest_folios_selected",
    )
    folio = next(item for item in folios if _folio_label(item) == selected_label)
    bill_no = str(folio.get("bill_no") or "")
    try:
        transactions = load_guest_folio_transactions(property_code, bill_no)
    except DatabaseConfigurationError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("The selected folio could not be loaded. Please try again.")
        return

    debit_total = sum(_as_amount(row.get("ft_debit")) for row in transactions)
    credit_total = sum(_as_amount(row.get("ft_credit")) for row in transactions)
    summary_columns = st.columns(4)
    summary_columns[0].metric("Guest", str(folio.get("display_name") or "-"))
    summary_columns[1].metric("Room", str(folio.get("room") or "-"))
    summary_columns[2].metric("Debits", _format_amount(debit_total))
    summary_columns[3].metric("Balance", _format_amount(debit_total - credit_total))

    frame = pd.DataFrame(transactions).rename(
        columns={
            "trx_no": "Transaction",
            "trx_code": "Code",
            "trx_date": "Date",
            "ft_debit": "Debit",
            "ft_credit": "Credit",
            "transaction_description": "Description",
        }
    )
    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Debit": st.column_config.NumberColumn(format="$%.2f"),
            "Credit": st.column_config.NumberColumn(format="$%.2f"),
        },
    )

    pdf_bytes = build_guest_folio_pdf(property_name, folio, transactions)
    download_column, email_column = st.columns(2)
    with download_column:
        st.download_button(
            "Download folio as PDF",
            data=pdf_bytes,
            file_name=f"guest_folio_{property_code}_{bill_no}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"guest_folios_pdf_{bill_no}",
        )
    with email_column:
        recipient = st.text_input(
            "Recipient email for simulation",
            value=_simulated_email(bill_no),
            help="Fictitious email generated for this folio. It can be edited for the simulation.",
            key=f"guest_folios_email_{bill_no}",
        ).strip()
        if st.button(
            "Simulate email delivery",
            disabled=not recipient,
            use_container_width=True,
            key=f"guest_folios_simulate_email_{bill_no}",
        ):
            st.success(
                f"Simulation complete: folio {bill_no} would be sent to {recipient}. No email was sent."
            )
