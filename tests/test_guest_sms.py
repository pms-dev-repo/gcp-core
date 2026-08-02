from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

with patch.dict("sys.modules", {"streamlit": object()}):
    from modules.guest_sms.page import (
        OPT_OUT_FOOTER,
        _available_dates,
        _demo_phone,
        _matches_segment,
        _personalize,
    )


class GuestSmsDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guest = {
            "id": "guest-101",
            "movement": "Arrivals",
            "first_name": "Elena",
            "stay": {
                "arrival_date": "Aug 01, 2026",
                "departure_date": "Aug 04, 2026",
            },
        }

    def test_segments_arrival_and_in_house(self) -> None:
        self.assertTrue(_matches_segment(self.guest, "Arrivals", date(2026, 8, 1)))
        self.assertFalse(_matches_segment(self.guest, "Arrivals", date(2026, 8, 2)))
        self.assertTrue(_matches_segment(self.guest, "In House", date(2026, 8, 2)))
        self.assertFalse(_matches_segment(self.guest, "Departures", date(2026, 8, 2)))

    def test_available_dates_are_unique_and_sorted(self) -> None:
        later_guest = {
            **self.guest,
            "id": "guest-102",
            "stay": {**self.guest["stay"], "arrival_date": "Aug 03, 2026"},
        }
        self.assertEqual(
            _available_dates([later_guest, self.guest, self.guest], "Arrivals"),
            [date(2026, 8, 1), date(2026, 8, 3)],
        )

    def test_personalization_always_includes_opt_out(self) -> None:
        message = _personalize(
            "Hi {{first_name}} from {{hotel_name}}.", self.guest, "GCP Hotel"
        )
        self.assertEqual(message, f"Hi Elena from GCP Hotel. {OPT_OUT_FOOTER}")

    def test_demo_phone_is_stable_and_fictional(self) -> None:
        self.assertEqual(_demo_phone(self.guest), _demo_phone(self.guest))
        self.assertIn(" 555 ", _demo_phone(self.guest))


if __name__ == "__main__":
    unittest.main()
