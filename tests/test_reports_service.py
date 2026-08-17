from __future__ import annotations

import unittest
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch


if "streamlit" not in sys.modules:
    streamlit_stub = ModuleType("streamlit")
    streamlit_stub.secrets = {}
    sys.modules["streamlit"] = streamlit_stub

if "supabase" not in sys.modules:
    supabase_stub = ModuleType("supabase")
    supabase_stub.Client = object
    supabase_stub.create_client = MagicMock()
    sys.modules["supabase"] = supabase_stub

from modules.reports import service


class ReportsServiceTests(unittest.TestCase):
    def test_report_property_code_uses_configured_property(self) -> None:
        self.assertEqual(
            service.report_property_code(
                "sandy_lane", {"reports": {"property_code": "SANDYL"}}
            ),
            "SANDYL",
        )

    def test_report_property_code_falls_back_to_client_code(self) -> None:
        self.assertEqual(service.report_property_code("GCPHOTEL", {}), "GCPHOTEL")

    @patch.object(service, "get_reports_supabase")
    def test_available_report_years_deduplicates_and_sorts(
        self, get_reports_supabase: MagicMock
    ) -> None:
        query = MagicMock()
        get_reports_supabase.return_value.table.return_value.select.return_value.eq.return_value = query
        query.execute.return_value.data = [
            {"calendar_year": 2025},
            {"calendar_year": "2026"},
            {"calendar_year": 2025},
            {"calendar_year": None},
        ]

        self.assertEqual(service.available_report_years("SANDYL"), [2026, 2025])

    @patch.object(service, "get_reports_supabase")
    def test_load_repeat_guest_monthly_filters_property_and_years(
        self, get_reports_supabase: MagicMock
    ) -> None:
        query = MagicMock()
        get_reports_supabase.return_value.table.return_value.select.return_value.eq.return_value.in_.return_value.order.return_value = query
        query.execute.return_value.data = [{"calendar_year": 2026, "calendar_month": 1}]

        rows = service.load_repeat_guest_monthly("SANDYL", [2026, 2025])

        self.assertEqual(rows, [{"calendar_year": 2026, "calendar_month": 1}])
        get_reports_supabase.return_value.table.assert_called_once_with(
            "rpt_repeat_guest_monthly"
        )

    @patch.object(service, "get_reports_supabase")
    def test_load_daily_figures_orders_the_source_rows(
        self, get_reports_supabase: MagicMock
    ) -> None:
        query = MagicMock()
        get_reports_supabase.return_value.table.return_value.select.return_value.order.return_value.order.return_value = query
        query.execute.return_value.data = [{"metric": "Rooms"}]

        rows = service.load_daily_figures()

        self.assertEqual(rows, [{"metric": "Rooms"}])
        get_reports_supabase.return_value.table.assert_called_once_with(
            "vw_daily_figures"
        )

    @patch.object(service, "get_reports_supabase")
    def test_load_statistics_manager_filters_the_active_property(
        self, get_reports_supabase: MagicMock
    ) -> None:
        query = MagicMock()
        get_reports_supabase.return_value.table.return_value.select.return_value.eq.return_value.order.return_value = query
        query.execute.return_value.data = [{"business_date": "2026-08-15"}]

        rows = service.load_statistics_manager("SANDYL")

        self.assertEqual(rows, [{"business_date": "2026-08-15"}])
        get_reports_supabase.return_value.table.assert_called_once_with(
            "rpt_statistics_manager"
        )

    @patch.object(service, "get_reports_supabase")
    def test_load_room_performance_orders_the_room_night_ranking(
        self, get_reports_supabase: MagicMock
    ) -> None:
        query = MagicMock()
        get_reports_supabase.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value = query
        query.execute.return_value.data = [{"room_number": "324", "room_nights": 1325}]

        rows = service.load_room_performance("SANDYL")

        self.assertEqual(rows, [{"room_number": "324", "room_nights": 1325}])
        get_reports_supabase.return_value.table.assert_called_once_with(
            "rpt_room_performance"
        )
