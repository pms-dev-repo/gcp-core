from __future__ import annotations

from collections import defaultdict

import streamlit as st

from core.config import (
    BASE_DIR,
    get_available_clients,
    get_default_client_code,
    load_client_config,
    module_enabled,
)
from core.module_registry import MODULES, ModuleDefinition
from utils.state import reset_client_state

SECTION_LABELS = {
    "main": "MAIN",
    "guest_documents": "GUEST COMMUNICATIONS",
    "front_office": "FRONT OFFICE",
    "management": "MANAGEMENT",
    "help": "HELP",
}


def _set_active_page(page_key: str) -> None:
    st.session_state.active_page = page_key
    st.rerun()


def _render_nav_content(module: ModuleDefinition, active: bool) -> None:
    st.markdown(
        f'<span class="sidebar-nav-marker {"active" if active else ""}"></span>',
        unsafe_allow_html=True,
    )

    if st.button(
        f"{module.icon}  {module.label}",
        key=f"sidebar_{module.key}",
        use_container_width=True,
        type="secondary",
    ):
        _set_active_page(module.key)


def _nav_button(module: ModuleDefinition, indented: bool = False) -> None:
    active = (
        st.session_state.get("active_page", "communications")
        == module.key
    )

    with st.container():
        if indented:
            _, button_col = st.columns([0.10, 0.90], gap="small")
            with button_col:
                _render_nav_content(module, active)
        else:
            _render_nav_content(module, active)


def _render_parent_label(parent: str) -> None:
    st.markdown(
        f"""
        <div class="gcp-guest-letters-parent">
            <span>✉&nbsp;&nbsp;{parent}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_branding() -> None:
    logo_path = BASE_DIR / "assets" / "gcp_logo_vector.svg"

    if logo_path.is_file():
        st.image(str(logo_path), width=220)
    else:
        st.markdown(
            '<div class="gcp-sidebar-logo-text">GCP</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="gcp-sidebar-product">'
        "Guest Communication Platform"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_hotel_selector() -> None:
    clients = get_available_clients()

    if not clients:
        st.error("No client configurations were found.")
        return

    code_to_name = {
        str(item["code"]): str(item["name"])
        for item in clients
    }
    codes = list(code_to_name)

    active_code = str(
        st.session_state.get(
            "active_client_code",
            get_default_client_code(),
        )
    )
    if active_code not in code_to_name:
        active_code = codes[0]
        st.session_state.active_client_code = active_code

    st.markdown(
        '<div class="gcp-hotel-selector-label">PROPERTY</div>',
        unsafe_allow_html=True,
    )

    selected_code = st.selectbox(
        "Active hotel",
        options=codes,
        index=codes.index(active_code),
        format_func=lambda code: code_to_name[code],
        key="hotel_selector",
        label_visibility="collapsed",
    )

    if selected_code != active_code:
        # Preserve the selected property after clearing property-specific state.
        reset_client_state()
        st.session_state.active_client_code = selected_code
        st.session_state.active_page = "communications"
        st.rerun()

    st.markdown(
        '<div class="gcp-sidebar-divider"></div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    _render_branding()
    _render_hotel_selector()

    client_code = str(
        st.session_state.get(
            "active_client_code",
            get_default_client_code(),
        )
    )
    config = load_client_config(client_code)

    visible = [
        module
        for module in MODULES
        if module_enabled(module.key, config)
    ]

    sections: dict[str, list[ModuleDefinition]] = defaultdict(list)
    for module in visible:
        sections[module.section].append(module)

    st.markdown(
        '<span class="gcp-sidebar-root"></span>',
        unsafe_allow_html=True,
    )

    for section_key in (
        "main",
        "guest_documents",
        "front_office",
        "management",
        "help",
    ):
        modules = sections.get(section_key, [])
        if not modules:
            continue

        st.markdown(
            f'<div class="gcp-sidebar-section-label">'
            f'{SECTION_LABELS[section_key]}'
            "</div>",
            unsafe_allow_html=True,
        )

        current_parent: str | None = None

        for module in modules:
            if module.parent and module.parent != current_parent:
                current_parent = module.parent
                _render_parent_label(current_parent)

            _nav_button(
                module,
                indented=bool(module.parent),
            )
