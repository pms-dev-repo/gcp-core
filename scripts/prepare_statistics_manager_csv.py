"""Normalize an OPERA Statistics Manager CSV for Supabase table import."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path


COLUMN_MAP = {
    "Business Date": "business_date",
    "Property": "property",
    "Arrival Rooms": "arrival_rooms",
    "Departure Rooms": "departure_rooms",
    "Individual Rooms": "individual_rooms",
    "Group Rooms": "group_rooms",
    "No-Show Rooms": "no_show_rooms",
    "Cancel Rooms": "cancel_rooms",
    "Walk-In Rooms": "walk_in_rooms",
    "House-Use Rooms": "house_use_rooms",
    "Day-Use Rooms": "day_use_rooms",
    "Complimentary Rooms": "complimentary_rooms",
    "Extended Stay Room": "extended_stay_rooms",
    "Occupancy %": "occupancy_pct",
    "Occupancy % (minus Complimentary & House Use)": "occupancy_pct_minus_complimentary_house_use",
    "Occupancy % (minus Complimentary, House User & Out-of-Order)": "occupancy_pct_minus_complimentary_house_use_out_of_order",
    "Occupied Rooms": "occupied_rooms",
    "Out of Order Rooms": "out_of_order_rooms",
    "Room Revenue": "room_revenue",
    "F&B Revenue": "fb_revenue",
    "Other Revenue": "other_revenue",
    "Total Revenue": "total_revenue",
    "Room Tax": "room_tax",
    "F&B Tax": "fb_tax",
    "Other Tax": "other_tax",
    "Total Tax": "total_tax",
}

INTEGER_COLUMNS = {
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
    "occupied_rooms",
    "out_of_order_rooms",
}


def normalize_number(value: str) -> str:
    return format(Decimal(value.replace(",", ".")), "f")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()

    with arguments.source.open(encoding="utf-8-sig", newline="") as source_file:
        source_rows = csv.DictReader(source_file, delimiter=";")
        arguments.destination.parent.mkdir(parents=True, exist_ok=True)
        with arguments.destination.open("w", encoding="utf-8", newline="") as destination_file:
            writer = csv.DictWriter(destination_file, fieldnames=list(COLUMN_MAP.values()))
            writer.writeheader()
            for source_row in source_rows:
                normalized: dict[str, str] = {}
                for source_name, target_name in COLUMN_MAP.items():
                    value = source_row[source_name].strip()
                    if target_name == "business_date":
                        normalized[target_name] = datetime.strptime(value, "%d/%m/%Y").date().isoformat()
                    elif target_name in INTEGER_COLUMNS:
                        normalized[target_name] = str(int(value))
                    elif target_name == "property":
                        normalized[target_name] = value
                    else:
                        normalized[target_name] = normalize_number(value)
                writer.writerow(normalized)


if __name__ == "__main__":
    main()
