from __future__ import annotations

import streamlit as st


# ==========================================================
# SIDEBAR VISIBILITY FLAGS
# Change any value to True when that module is ready.
# ==========================================================

# MAIN
SHOW_DASHBOARD = False
SHOW_HISTORY = False

# GUEST LETTERS SUBMENU
SHOW_ARRIVALS_DEPARTURES = True
SHOW_BIRTHDAYS = False
SHOW_ANNIVERSARIES = False
SHOW_VIP_GUESTS = False
SHOW_SPECIAL_EVENTS = False
SHOW_ROOM_READY = False
SHOW_ROOM_UPGRADES = False

# MANAGEMENT
SHOW_TEMPLATES = True
SHOW_ADMINISTRATION = True
SHOW_SETTINGS = False

# HELP
SHOW_HELP = False
SHOW_ABOUT = True

# OPTIONAL SIDEBAR ELEMENTS
SHOW_BRANDING = False
SHOW_SEARCH = False


PRIMARY_ITEMS = [
    ("▣", "Dashboard", "dashboard", SHOW_DASHBOARD),
    ("◷", "Communication History", "history", SHOW_HISTORY),
]

GUEST_LETTER_ITEMS = [
    ("✈", "Arrivals and Departures", "communications", SHOW_ARRIVALS_DEPARTURES),
    ("🎂", "Birthdays", "birthdays", SHOW_BIRTHDAYS),
    ("💍", "Anniversaries", "anniversaries", SHOW_ANNIVERSARIES),
    ("★", "VIP Guests", "vip_guests", SHOW_VIP_GUESTS),
    ("🎉", "Special Events", "special_events", SHOW_SPECIAL_EVENTS),
    ("🔔", "Room Ready", "room_ready", SHOW_ROOM_READY),
    ("⬆", "Room Upgrades", "room_upgrades", SHOW_ROOM_UPGRADES),
]

ADMIN_ITEMS = [
    ("⚙", "Administration", "administration", SHOW_ADMINISTRATION),
    ("▤", "Template Studio", "templates", SHOW_TEMPLATES),
    ("◉", "Settings", "settings", SHOW_SETTINGS),
]

HELP_ITEMS = [
    ("?", "Help", "help", SHOW_HELP),
    ("ⓘ", "About GCP", "about", SHOW_ABOUT),
]


def _visible_items(
    items: list[tuple[str, str, str, bool]],
) -> list[tuple[str, str, str]]:
    return [
        (icon, label, page_key)
        for icon, label, page_key, visible in items
        if visible
    ]


def _set_active_page(page_key: str) -> None:
    st.session_state.active_page = page_key
    st.rerun()


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
        _set_active_page(page_key)


def _submenu_button(icon: str, label: str, page_key: str) -> None:
    active = st.session_state.get("active_page", "communications") == page_key

    _, button_col = st.columns([0.10, 0.90], gap="small")

    with button_col:
        st.markdown(
            f'<span class="sidebar-nav-marker {"active" if active else ""}"></span>',
            unsafe_allow_html=True,
        )

        if st.button(
            f"{icon}  {label}",
            key=f"sidebar_submenu_{page_key}",
            use_container_width=True,
            type="secondary",
        ):
            _set_active_page(page_key)


def _render_guest_letters_group(
    items: list[tuple[str, str, str]],
) -> None:
    if not items:
        return

    # Some global themes use -webkit-text-fill-color, which can override
    # normal `color`. Set both properties on the parent and every child.
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] .gcp-guest-letters-parent,
        section[data-testid="stSidebar"] .gcp-guest-letters-parent *,
        [data-testid="stSidebar"] .gcp-guest-letters-parent,
        [data-testid="stSidebar"] .gcp-guest-letters-parent * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
        }
        </style>

        <div class="gcp-guest-letters-parent" style="
            margin-top:5px;
            margin-bottom:5px;
            padding:8px 10px 5px 10px;
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            font-size:14px;
            font-weight:700;
            line-height:1.25;
            letter-spacing:0.01em;
            opacity:1 !important;
        ">
            <span style="
                color:#ffffff !important;
                -webkit-text-fill-color:#ffffff !important;
                opacity:1 !important;
            ">✉&nbsp;&nbsp;Guest Letters</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for item in items:
        _submenu_button(*item)


def render_sidebar() -> None:
    primary_items = _visible_items(PRIMARY_ITEMS)
    guest_letter_items = _visible_items(GUEST_LETTER_ITEMS)
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
                    <div class="gcp-sidebar-brand-subtitle">
                        Communication Platform
                    </div>
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

    if primary_items or guest_letter_items:
        st.markdown(
            '<div class="gcp-sidebar-section-label">MAIN</div>',
            unsafe_allow_html=True,
        )

        for item in primary_items:
            _nav_button(*item)

        _render_guest_letters_group(guest_letter_items)

    if admin_items:
        st.markdown(
            '<div class="gcp-sidebar-section-label '
            'gcp-sidebar-section-spaced">MANAGEMENT</div>',
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
