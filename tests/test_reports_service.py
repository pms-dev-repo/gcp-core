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

    @patch.object(service, "get_supabase")
    def test_available_report_years_deduplicates_and_sorts(self, get_supabase: MagicMock) -> None:
        query = MagicMock()
        get_supabase.return_value.table.return_value.select.return_value.eq.return_value = query
        query.execute.return_value.data = [
            {"calendar_year": 2025},
            {"calendar_year": "2026"},
            {"calendar_year": 2025},
            {"calendar_year": None},
        ]

        self.assertEqual(service.available_report_years("SANDYL"), [2026, 2025])

    @patch.object(service, "get_supabase")
    def test_load_repeat_guest_monthly_filters_property_and_years(self, get_supabase: MagicMock) -> None:
        query = MagicMock()
        get_supabase.return_value.table.return_value.select.return_value.eq.return_value.in_.return_value.order.return_value = query
        query.execute.return_value.data = [{"calendar_year": 2026, "calendar_month": 1}]

        rows = service.load_repeat_guest_monthly("SANDYL", [2026, 2025])

        self.assertEqual(rows, [{"calendar_year": 2026, "calendar_month": 1}])
        get_supabase.return_value.table.assert_called_once_with("rpt_repeat_guest_monthly")
