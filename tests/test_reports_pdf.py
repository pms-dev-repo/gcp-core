from __future__ import annotations

import sys
import unittest
from types import ModuleType
from unittest.mock import MagicMock


if "streamlit" not in sys.modules:
    streamlit_stub = ModuleType("streamlit")
    streamlit_stub.secrets = {}
    sys.modules["streamlit"] = streamlit_stub

if "supabase" not in sys.modules:
    supabase_stub = ModuleType("supabase")
    supabase_stub.Client = object
    supabase_stub.create_client = MagicMock()
    sys.modules["supabase"] = supabase_stub

import pandas as pd

from modules.reports.page import _revenue_comparison_table, build_repeat_guest_report_pdf


class ReportsPdfTests(unittest.TestCase):
    def test_revenue_comparison_calculates_new_repeat_and_total(self) -> None:
        table = _revenue_comparison_table(
            [
                {
                    "calendar_year": 2026,
                    "calendar_month": 1,
                    "repeat_room_revenue": 120,
                    "new_room_revenue": 80,
                },
                {
                    "calendar_year": 2025,
                    "calendar_month": 1,
                    "repeat_room_revenue": 100,
                    "new_room_revenue": 50,
                },
            ],
            2026,
            2025,
            1,
            1,
            "room_revenue",
        )

        self.assertEqual(table.iloc[0]["YOY Repeat"], 20)
        self.assertEqual(table.iloc[0]["YOY New"], 30)
        self.assertEqual(table.iloc[1]["2026 Repeat"], 120)
        self.assertEqual(table.iloc[1]["2026 New"], 80)

    def test_repeat_guest_report_pdf_is_generated(self) -> None:
        report = pd.DataFrame(
            [
                {
                    "Month": "Jan",
                    "2026 Repeat": 12,
                    "% Repeat": 0.4,
                    "2025 Repeat": 15,
                    "% Repeat prior": 0.5,
                    "YOY Repeat": -3,
                    "YOY Repeat %": -0.1,
                    "2026 New": 18,
                    "% New": 0.6,
                    "2025 New": 15,
                    "% New prior": 0.5,
                    "YOY New": 3,
                    "YOY New %": 0.1,
                }
            ]
        )

        pdf = build_repeat_guest_report_pdf(
            "Sandy Lane", 2026, 2025, 1, 1, report, report
        )

        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1_000)
