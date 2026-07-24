from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "guests.json"


@st.cache_data
def load_guests() -> list[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)["guests"]


def get_guest_by_id(guests: list[dict[str, Any]], guest_id: str) -> dict[str, Any]:
    return next(guest for guest in guests if guest["id"] == guest_id)
