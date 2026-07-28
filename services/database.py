from __future__ import annotations

from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


class DatabaseConfigurationError(RuntimeError):
    """Raised when Supabase is not configured correctly."""


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a cached Supabase client configured from Streamlit Secrets."""
    try:
        url = str(st.secrets["SUPABASE_URL"]).strip()
        key = str(st.secrets["SUPABASE_SECRET_KEY"]).strip()
    except KeyError as exc:
        raise DatabaseConfigurationError(
            "Missing SUPABASE_URL or SUPABASE_SECRET_KEY in Streamlit Secrets."
        ) from exc

    if not url or not key:
        raise DatabaseConfigurationError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY cannot be empty."
        )

    return create_client(url, key)
