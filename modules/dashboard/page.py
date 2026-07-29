from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any

import streamlit as st

from core.config import get_active_client_code, load_client_config, module_enabled


MODULE_META: dict[str, dict[str, str]] = {
    "communications": {
        "icon": "✉",
        "title": "Guest Communications",
        "description": "Arrival and departure communications",
    },
    "confirmation_letters": {
        "icon": "✓",
        "title": "Confirmation Letters",
        "description": "Reservation confirmations and cancellations",
    },
    "registration_cards": {
        "icon": "▣",
        "title": "Registration Cards",
        "description": "Pre-arrival registration workflow",
    },
    "guest_transportation": {
        "icon": "🚐",
        "title": "Guest Transportation",
        "description": "Daily pickups, drop-offs and transfer operations",
    },
    "history": {
        "icon": "◷",
        "title": "Document History",
        "description": "Generated and sent document activity",
    },
    "templates": {
        "icon": "▤",
        "title": "Template Studio",
        "description": "Manage property document templates",
    },
    "administration": {
        "icon": "⚙",
        "title": "Administration",
        "description": "Users, configuration and controls",
    },
}


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _movement(guest: dict[str, Any]) -> str:
    return _normalize(guest.get("movement"))


def _email(guest: dict[str, Any]) -> str:
    return str(guest.get("email") or "").strip()


def _status(guest: dict[str, Any], *paths: tuple[str, ...]) -> str:
    for path in paths:
        current: Any = guest
        for key in path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if current not in (None, ""):
            return _normalize(current)
    return ""


def _count_status(guests: list[dict[str, Any]], accepted: set[str], *paths: tuple[str, ...]) -> int:
    return sum(1 for guest in guests if _status(guest, *paths) in accepted)


def _registration_metrics(guests: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
    generated = _count_status(
        guests,
        {"generated", "reviewed", "sent", "signed", "completed"},
        ("registration_card", "status"),
        ("document", "status"),
    )
    signed = _count_status(
        guests,
        {"signed", "completed"},
        ("registration_card", "status"),
        ("registration", "status"),
    )
    pending = max(len(guests) - generated, 0)
    return [("Pending", pending, "pending"), ("Generated", generated, "generated"), ("Signed", signed, "sent")]


def _confirmation_metrics(guests: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
    cancelled = [g for g in guests if _movement(g) in {"cancelled", "canceled", "cancellation", "cancellations"} or g.get("cancellation_date")]
    confirmations = [g for g in guests if g not in cancelled]
    generated = _count_status(
        confirmations,
        {"generated", "reviewed", "sent", "completed"},
        ("communications", "confirmation_letter"),
        ("confirmation", "status"),
        ("document", "status"),
    )
    sent = _count_status(
        confirmations,
        {"sent", "completed"},
        ("communications", "confirmation_letter"),
        ("confirmation", "status"),
        ("communication", "status"),
    )
    pending = max(len(confirmations) - generated, 0)
    return [("Pending", pending, "pending"), ("Generated", generated, "generated"), ("Sent", sent, "sent"), ("Cancelled", len(cancelled), "cancelled")]


def _communication_metrics(guests: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
    movements = Counter(_movement(g) for g in guests)
    arrivals = sum(movements[key] for key in ("arrival", "arrivals"))
    departures = sum(movements[key] for key in ("departure", "departures"))
    sent = _count_status(
        guests,
        {"sent", "completed"},
        ("communication", "status"),
        ("document", "status"),
    )
    missing_email = sum(1 for guest in guests if not _email(guest))
    return [("Arrivals", arrivals, "arrival"), ("Departures", departures, "departure"), ("Sent", sent, "sent"), ("Missing email", missing_email, "warning")]


def _transportation_metrics(guests: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
    transfers = [
        guest
        for guest in guests
        if str((guest.get("transport") or {}).get("transfer") or "").strip()
        not in {"", "None"}
    ]
    arrivals = sum(1 for guest in transfers if _movement(guest) in {"arrival", "arrivals"})
    departures = sum(1 for guest in transfers if _movement(guest) in {"departure", "departures"})
    assigned = sum(
        1
        for guest in transfers
        if str((guest.get("transport") or {}).get("transfer") or "").strip()
        not in {"", "None"}
    )
    return [
        ("Transfers", len(transfers), "generated"),
        ("Arrivals", arrivals, "arrival"),
        ("Departures", departures, "departure"),
        ("Assigned", assigned, "sent"),
    ]


def _open_module(module_key: str) -> None:
    st.session_state.active_page = module_key
    st.rerun()


def _metric_tile(label: str, value: int, tone: str) -> str:
    return (
        f'<div class="dashboard-metric dashboard-metric-{escape(tone)}">'
        f'<div class="dashboard-metric-label">{escape(label)}</div>'
        f'<div class="dashboard-metric-value">{value:,}</div>'
        "</div>"
    )


def _render_module_card(module_key: str, metrics: list[tuple[str, int, str]]) -> None:
    meta = MODULE_META[module_key]
    with st.container(border=True):
        st.markdown('<span class="dashboard-card-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="dashboard-card-heading">
                <div class="dashboard-card-icon">{escape(meta['icon'])}</div>
                <div>
                    <div class="dashboard-card-title">{escape(meta['title'])}</div>
                    <div class="dashboard-card-description">{escape(meta['description'])}</div>
                </div>
            </div>
            <div class="dashboard-card-metrics">
                {''.join(_metric_tile(label, value, tone) for label, value, tone in metrics)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open module  →", key=f"dashboard_open_{module_key}", use_container_width=True):
            _open_module(module_key)


def _render_quick_link(module_key: str) -> None:
    meta = MODULE_META[module_key]
    with st.container(border=True):
        st.markdown('<span class="dashboard-quick-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="dashboard-quick-heading">
                <span class="dashboard-quick-icon">{escape(meta['icon'])}</span>
                <div>
                    <div class="dashboard-quick-title">{escape(meta['title'])}</div>
                    <div class="dashboard-quick-description">{escape(meta['description'])}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open", key=f"dashboard_quick_{module_key}", use_container_width=True):
            _open_module(module_key)


def render(guests: list[dict[str, Any]] | None = None) -> None:
    guests = guests or []
    client_code = get_active_client_code()
    config = load_client_config(client_code)
    client = config.get("client", {})
    hotel_name = str(client.get("name") or "Property")

    st.markdown(
        f"""
        <section class="dashboard-hero">
            <div>
                <div class="dashboard-eyebrow">EXECUTIVE WORKSPACE</div>
                <h1>Good day, {escape(hotel_name)}</h1>
                <p>Your active modules and today's operational workload in one place.</p>
            </div>
            <div class="dashboard-property-chip">● Live property</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    operational: list[tuple[str, list[tuple[str, int, str]]]] = []
    if module_enabled("communications", config):
        operational.append(("communications", _communication_metrics(guests)))
    if module_enabled("confirmation_letters", config):
        operational.append(("confirmation_letters", _confirmation_metrics(guests)))
    if module_enabled("registration_cards", config):
        operational.append(("registration_cards", _registration_metrics(guests)))
    if module_enabled("guest_transportation", config):
        operational.append(("guest_transportation", _transportation_metrics(guests)))

    if operational:
        st.markdown('<div class="dashboard-section-title">Operational modules</div>', unsafe_allow_html=True)
        columns = st.columns(min(len(operational), 3), gap="large")
        for index, (module_key, metrics) in enumerate(operational):
            with columns[index % len(columns)]:
                _render_module_card(module_key, metrics)

    quick_modules = [
        key for key in ("history", "templates", "administration")
        if module_enabled(key, config)
    ]
    if quick_modules:
        st.markdown('<div class="dashboard-section-title dashboard-section-spaced">Management tools</div>', unsafe_allow_html=True)
        columns = st.columns(min(len(quick_modules), 3), gap="large")
        for index, module_key in enumerate(quick_modules):
            with columns[index % len(columns)]:
                _render_quick_link(module_key)

    if not operational and not quick_modules:
        st.info("No dashboard cards are available because no supported modules are enabled for this property.")
