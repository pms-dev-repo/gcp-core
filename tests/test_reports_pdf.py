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

from modules.reports.page import build_repeat_guest_report_pdf


class ReportsPdfTests(unittest.TestCase):
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
