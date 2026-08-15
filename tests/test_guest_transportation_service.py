from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.guest_transportation_service import load_transportation_guests


class _Query:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class _Client:
    def __init__(self, tables: dict[str, list[dict[str, object]]]) -> None:
        self.tables = tables

    def table(self, name: str) -> _Query:
        return _Query(self.tables.get(name, []))


class GuestTransportationServiceTests(unittest.TestCase):
    def test_loads_daily_views_and_merges_saved_assignment(self) -> None:
        arrival = {
            "client_code": "GCPHOTEL",
            "guest_name": "Example,Guest",
            "confirmation_no": 12345,
            "room_no": 101,
            "arrival_date": "2026-08-15",
            "departure_date": "2026-08-18",
            "adults": 2,
            "children": 1,
            "transport_direction": "PICKUP",
            "transport_time": "14:30",
            "transport_flight": "AA585",
            "destination_airport": "Grantley Adams International",
            "destination_iata": "BGI",
        }
        initial_client = _Client(
            {
                "vw_daily_arrivals_transportation": [arrival],
                "vw_daily_departures_transportation": [],
                "guest_transportation_assignments": [],
            }
        )
        with patch(
            "services.guest_transportation_service.get_supabase",
            return_value=initial_client,
        ):
            initial = load_transportation_guests("GCPHOTEL")

        record_key = initial[0]["id"]
        initial_client.tables["guest_transportation_assignments"] = [
            {
                "record_key": record_key,
                "client_code": "GCPHOTEL",
                "status": "Assigned",
                "driver": "Demo Driver",
            }
        ]
        with patch(
            "services.guest_transportation_service.get_supabase",
            return_value=initial_client,
        ):
            guests = load_transportation_guests("GCPHOTEL")

        self.assertEqual(len(guests), 1)
        self.assertEqual(guests[0]["movement"], "Arrivals")
        self.assertEqual(guests[0]["transport"]["transfer"], "Airport pickup")
        self.assertEqual(guests[0]["transport"]["flight"], "AA585")
        self.assertEqual(
            guests[0]["transport"]["pickup_location"],
            "Grantley Adams International (BGI)",
        )
        self.assertEqual(guests[0]["transport_assignment"]["status"], "Assigned")


if __name__ == "__main__":
    unittest.main()
