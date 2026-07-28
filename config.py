from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
CLIENTS_DIR = BASE_DIR / "config" / "clients"
DEFAULT_CLIENT = "sandy_lane"


class ConfigurationError(RuntimeError):
    """Raised when a client configuration cannot be loaded."""


def get_available_clients() -> list[dict[str, str]]:
    """Return all valid client configurations available to the UI."""
    clients: list[dict[str, str]] = []

    if not CLIENTS_DIR.exists():
        return clients

    for path in sorted(CLIENTS_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        client = payload.get("client", {})
        code = str(client.get("code") or path.stem)
        name = str(client.get("name") or code.replace("_", " ").title())
        clients.append({"code": code, "name": name})

    return clients


def get_default_client_code() -> str:
    configured = os.getenv("GCP_CLIENT", DEFAULT_CLIENT)
    valid_codes = {item["code"] for item in get_available_clients()}

    if configured in valid_codes:
        return configured
    if DEFAULT_CLIENT in valid_codes:
        return DEFAULT_CLIENT
    return next(iter(valid_codes), configured)


def get_active_client_code() -> str:
    """Read the selected client from Streamlit state when available."""
    try:
        import streamlit as st

        return str(st.session_state.get("active_client_code") or get_default_client_code())
    except Exception:
        return get_default_client_code()


@lru_cache(maxsize=32)
def load_client_config(client_code: str | None = None) -> dict[str, Any]:
    code = client_code or get_active_client_code()
    path = CLIENTS_DIR / f"{code}.json"

    if not path.is_file():
        raise ConfigurationError(
            f"Client configuration not found: {path}. "
            "Select a valid hotel or set GCP_CLIENT to a valid client code."
        )

    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Invalid client configuration: {path}") from exc

    config.setdefault("client", {})
    config.setdefault("modules", {})
    config.setdefault("document_types", {})
    config["client"].setdefault("code", code)
    config["client"].setdefault("data_folder", code)
    config["client"].setdefault("templates_folder", code)
    return config


def module_enabled(module_key: str, config: dict[str, Any] | None = None) -> bool:
    active_config = config or load_client_config()
    return bool(active_config.get("modules", {}).get(module_key, False))


def enabled_modules(config: dict[str, Any] | None = None) -> set[str]:
    active_config = config or load_client_config()
    return {
        key
        for key, enabled in active_config.get("modules", {}).items()
        if enabled
    }
