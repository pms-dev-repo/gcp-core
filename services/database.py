from __future__ import annotations

from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


class DatabaseConfigurationError(RuntimeError):
    """Raised when Supabase is not configured correctly."""


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return the default GCP-db Supabase client."""
    return _get_supabase_client("SUPABASE_URL", "SUPABASE_SECRET_KEY", "GCP-db")


@lru_cache(maxsize=1)
def get_reports_supabase() -> Client:
    """Return the dedicated OPERA DataHub Supabase client for Reports."""
    return _get_supabase_client(
        "REPORTS_SUPABASE_URL",
        "REPORTS_SUPABASE_SECRET_KEY",
        "OPERA-DATAHUB-EXPRESS",
    )


def _get_supabase_client(url_secret: str, key_secret: str, database_name: str) -> Client:
    """Create a Supabase client from an explicit pair of Streamlit secrets."""
    try:
        url = str(st.secrets[url_secret]).strip()
        key = str(st.secrets[key_secret]).strip()
    except KeyError as exc:
        raise DatabaseConfigurationError(
            f"Missing {url_secret} or {key_secret} for {database_name} in Streamlit Secrets."
        ) from exc

    if not url or not key:
        raise DatabaseConfigurationError(
            f"{url_secret} and {key_secret} for {database_name} cannot be empty."
        )

    return create_client(url, key)
