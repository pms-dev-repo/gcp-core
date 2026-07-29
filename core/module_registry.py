from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ModuleDefinition:
    key: str
    label: str
    icon: str
    section: str
    renderer: Callable[[], None] | None = None
    parent: str | None = None


MODULES = (
    ModuleDefinition("dashboard", "Dashboard", "▣", "main"),
    ModuleDefinition(
        "communications",
        "Guest Letters",
        "✉",
        "guest_documents",
        parent="Guest Communications",
    ),
    ModuleDefinition(
        "confirmation_letters",
        "Confirmation Letters",
        "✉",
        "guest_documents",
        parent="Guest Communications",
    ),
    ModuleDefinition(
        "registration_cards",
        "Registration Cards",
        "▤",
        "front_office",
        parent="Front Office",
    ),
    ModuleDefinition(
        "guest_transportation",
        "Guest Transportation",
        "🚐",
        "front_office",
        parent="Front Office",
    ),
    ModuleDefinition(
        "flight_center",
        "Flight Center",
        "✈",
        "front_office",
        parent="Front Office",
    ),
    ModuleDefinition("history", "Document History", "◷", "main"),
    ModuleDefinition("administration", "Administration", "⚙", "management"),
    ModuleDefinition("templates", "Template Studio", "▤", "management"),
    ModuleDefinition("settings", "Settings", "◉", "management"),
    ModuleDefinition("about", "About GCP", "ⓘ", "help"),
)


def get_module(module_key: str) -> ModuleDefinition | None:
    return next((module for module in MODULES if module.key == module_key), None)
