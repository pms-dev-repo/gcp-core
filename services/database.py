from __future__ import annotations

from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


class DatabaseConfigurationError(RuntimeError):
    """Raised when Supabase is not configured correctly."""


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SECRET_KEY"]
    except KeyError as exc:
        raise DatabaseConfigurationError(
            "Missing SUPABASE_URL or SUPABASE_SECRET_KEY in Streamlit Secrets."
        ) from exc

    return create_client(url, key)