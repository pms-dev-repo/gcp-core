"""Normalize an OPERA R&A guest-folio export for rpt_guest_folio_details."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


TARGET_FIELDS = [
    "property",
    "folio_type",
    "bill_no",
    "bill_generation_date",
    "bill_generation_date_char",
    "fiscal_bill_no",
    "status",
    "room",
    "display_name",
    "sumft_debit_per_bill_no",
    "sumft_credit_per_bill_no",
    "trx_no",
    "trx_code",
    "trx_date",
    "ft_debit",
    "ft_credit",
    "transaction_description",
    "source_file",
]


def clean(value: str | None) -> str:
    return (value or "").strip()


def iso_date(value: str | None) -> str:
    raw_value = clean(value)
    if not raw_value:
        return ""
    return datetime.strptime(raw_value, "%d-%b-%y").date().isoformat()


def number(value: str | None) -> str:
    raw_value = clean(value).replace(",", "")
    return raw_value


def transform_row(row: dict[str, str | None], property_code: str, source_file: str) -> dict[str, str]:
    return {
        "property": property_code,
        "folio_type": clean(row.get("FOLIO_TYPE")),
        "bill_no": clean(row.get("BILL_NO")),
        "bill_generation_date": iso_date(row.get("BILL_GENERATION_DATE")),
        "bill_generation_date_char": clean(row.get("BILL_GENERATION_DATE_CHAR")),
        "fiscal_bill_no": clean(row.get("FISCAL_BILL_NO")),
        "status": clean(row.get("STATUS")),
        "room": clean(row.get("ROOM")),
        "display_name": clean(row.get("DISPLAY_NAME")),
        "sumft_debit_per_bill_no": number(row.get("SUMFT_DEBITPERBILL_NO")),
        "sumft_credit_per_bill_no": number(row.get("SUMFT_CREDITPERBILL_NO")),
        "trx_no": clean(row.get("TRX_NO")),
        "trx_code": clean(row.get("TRX_CODE")),
        "trx_date": iso_date(row.get("TRX_DATE")),
        "ft_debit": number(row.get("FT_DEBIT")),
        "ft_credit": number(row.get("FT_CREDIT")),
        "transaction_description": clean(row.get("TRANSACTION_DESCRIPTION")),
        "source_file": source_file,
    }


def source_row_to_mapping(row: list[str]) -> dict[str, str]:
    """Handle R&A's unquoted `Last name, First name` display-name field.

    The export header describes 16 fields, but its data rows contain an extra
    comma whenever DISPLAY_NAME is formatted as `Last name, First name`.
    The fields before and after the name are stable, so rebuild that row before
    applying the normal column transformation.
    """
    if len(row) < 16:
        return {}
    prefix = row[:7]
    suffix = row[-8:]
    display_name = ",".join(part.strip() for part in row[7:-8] if part.strip())
    values = prefix + [display_name] + suffix
    source_fields = [
        "FOLIO_TYPE",
        "BILL_NO",
        "BILL_GENERATION_DATE",
        "BILL_GENERATION_DATE_CHAR",
        "FISCAL_BILL_NO",
        "STATUS",
        "ROOM",
        "DISPLAY_NAME",
        "SUMFT_DEBITPERBILL_NO",
        "SUMFT_CREDITPERBILL_NO",
        "TRX_NO",
        "TRX_CODE",
        "TRX_DATE",
        "FT_DEBIT",
        "FT_CREDIT",
        "TRANSACTION_DESCRIPTION",
    ]
    return dict(zip(source_fields, values, strict=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--property", required=True)
    args = parser.parse_args()

    with args.input_csv.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        next(reader, None)
        rows = [
            transform_row(source_row_to_mapping(row), args.property.strip(), args.input_csv.name)
            for row in reader
            if clean(source_row_to_mapping(row).get("BILL_NO"))
        ]

    with args.output_csv.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=TARGET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Prepared {len(rows)} folio transaction rows in {args.output_csv}")


if __name__ == "__main__":
    main()
