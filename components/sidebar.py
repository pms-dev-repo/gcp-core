from __future__ import annotations

import streamlit as st


# ==========================================================
# TEMPORARY SIDEBAR VISIBILITY FLAGS
# Change any value to True when that module is ready.
# ==========================================================

SHOW_DASHBOARD = False
SHOW_TEMPLATES = False
SHOW_HISTORY = False
SHOW_ADMINISTRATION = True
SHOW_SETTINGS = False
SHOW_HELP = True
SHOW_ABOUT = True

SHOW_BRANDING = False
SHOW_SEARCH = False


PRIMARY_ITEMS = [
    ("▣", "Dashboard", "dashboard", SHOW_DASHBOARD),
    ("✉", "Guest Communications", "communications", True),
    ("▤", "Templates", "templates", SHOW_TEMPLATES),
    ("◷", "Communication History", "history", SHOW_HISTORY),
]

ADMIN_ITEMS = [
    ("⚙", "Administration", "administration", SHOW_ADMINISTRATION),
    ("◉", "Settings", "settings", SHOW_SETTINGS),
]

HELP_ITEMS = [
    ("?", "Help", "help", SHOW_HELP),
    ("ⓘ", "About GCP", "about", SHOW_ABOUT),
]


def _nav_button(icon: str, label: str, page_key: str) -> None:
    active = st.session_state.get("active_page", "communications") == page_key

    st.markdown(
        f'<span class="sidebar-nav-marker {"active" if active else ""}"></span>',
        unsafe_allow_html=True,
    )

    if st.button(
        f"{icon}  {label}",
        key=f"sidebar_{page_key}",
        use_container_width=True,
        type="secondary",
    ):
        st.session_state.active_page = page_key
        st.rerun()


def _visible_items(items: list[tuple[str, str, str, bool]]) -> list[tuple[str, str, str]]:
    return [
        (icon, label, page_key)
        for icon, label, page_key, visible in items
        if visible
    ]


def render_sidebar() -> None:
    primary_items = _visible_items(PRIMARY_ITEMS)
    admin_items = _visible_items(ADMIN_ITEMS)
    help_items = _visible_items(HELP_ITEMS)

    st.markdown('<span class="gcp-sidebar-root"></span>', unsafe_allow_html=True)

    if SHOW_BRANDING:
        st.markdown(
            """
            <div class="gcp-sidebar-brand">
                <div class="gcp-sidebar-brand-icon">G</div>
                <div>
                    <div class="gcp-sidebar-brand-title">GCP</div>
                    <div class="gcp-sidebar-brand-subtitle">Communication Platform</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if SHOW_SEARCH:
        st.markdown(
            """
            <div class="gcp-sidebar-search">
                <span>⌕</span>
                <div>Search</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not SHOW_BRANDING and not SHOW_SEARCH:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if primary_items:
        st.markdown(
            '<div class="gcp-sidebar-section-label">MAIN</div>',
            unsafe_allow_html=True,
        )

        for item in primary_items:
            _nav_button(*item)

    if admin_items:
        st.markdown(
            '<div class="gcp-sidebar-section-label gcp-sidebar-section-spaced">'
            'MANAGEMENT'
            '</div>',
            unsafe_allow_html=True,
        )

        for item in admin_items:
            _nav_button(*item)

    if help_items:
        st.markdown(
            '<div class="gcp-sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        for item in help_items:
            _nav_button(*item)
