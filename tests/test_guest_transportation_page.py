from __future__ import annotations

import unittest
from unittest.mock import MagicMock, call, patch

from modules.guest_transportation import page


class GuestTransportationPageTests(unittest.TestCase):
    def test_render_separates_arrivals_departures_and_board(self) -> None:
        guests = [{"id": "example"}]
        fake_streamlit = MagicMock()
        fake_streamlit.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        config = {
            "client": {"name": "Sandy Lane"},
            "guest_transportation": {"data_client_code": "GCPHOTEL"},
        }

        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(page, "get_active_client_code", return_value="sandy_lane"),
            patch.object(page, "load_client_config", return_value=config),
            patch.object(page, "load_transportation_guests", return_value=guests),
            patch.object(page, "_render_direction_workflow") as render_workflow,
            patch.object(page, "_render_operational_board") as render_board,
        ):
            page.render()

        fake_streamlit.tabs.assert_called_once_with(
            ["Arrivals", "Departures", "Operational Board"]
        )
        self.assertEqual(
            render_workflow.call_args_list,
            [
                call(guests, "GCPHOTEL", "Arrival"),
                call(guests, "GCPHOTEL", "Departure"),
            ],
        )
        render_board.assert_called_once_with(guests, "GCPHOTEL")


if __name__ == "__main__":
    unittest.main()
