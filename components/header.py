from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import streamlit as st
import streamlit.components.v1 as components

from core.config import BASE_DIR, load_client_config


def _render_sidebar_toggle_script() -> None:
    components.html(
        """
        <script>
        (() => {
            const parentDocument = window.parent.document;

            function installToggle() {
                const header = parentDocument.querySelector(".gcp-header");
                const sidebar = parentDocument.querySelector('[data-testid="stSidebar"]');

                if (!header || !sidebar) {
                    window.setTimeout(installToggle, 80);
                    return;
                }

                let button = header.querySelector(".gcp-header-menu-button");
                if (!button) {
                    button = parentDocument.createElement("button");
                    button.type = "button";
                    button.className = "gcp-header-menu-button";
                    button.setAttribute("aria-label", "Show or hide navigation");
                    button.setAttribute("title", "Show or hide navigation");
                    header.prepend(button);
                }

                function refreshIcon() {
                    const collapsed = parentDocument.body.classList.contains("gcp-sidebar-collapsed");
                    button.textContent = "☰";
                    button.setAttribute("aria-expanded", String(!collapsed));
                }

                button.onclick = () => {
                    parentDocument.body.classList.toggle("gcp-sidebar-collapsed");
                    refreshIcon();
                };

                refreshIcon();
            }

            installToggle();
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_header() -> None:
    config = load_client_config()
    client = config.get("client", {})
    branding = client.get("branding", {})

    timezone_name = str(client.get("timezone") or config.get("timezone") or "UTC")

    try:
        local_now = datetime.now(ZoneInfo(timezone_name))
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        local_now = datetime.now(ZoneInfo("UTC"))

    date_text = local_now.strftime("%A, %d %b, %Y")
    time_text = local_now.strftime("%I:%M %p").lstrip("0")
    timezone_abbr = local_now.tzname() or "UTC"

    product_name = escape(str(branding.get("product_name", "GCP")))
    product_subtitle = escape(str(branding.get("product_subtitle", "Guest Communication Platform")))
    hotel_name = escape(str(client.get("name", "Hotel")).upper())

    logo_path = BASE_DIR / "assets" / "gcp_logo_vector.svg"
    try:
        logo_data = b64encode(logo_path.read_bytes()).decode("ascii")
        brand_html = (
            '<img class="gcp-brand-logo" '
            f'src="data:image/svg+xml;base64,{logo_data}" '
            f'alt="{product_name}" />'
        )
    except OSError:
        brand_html = f'<div class="gcp-brand">{product_name}</div>'

    header_html = (
        '<div class="gcp-header">'
        '<div class="gcp-header-left">'
        f'{brand_html}'
        '<div class="gcp-divider"></div>'
        f'<div class="gcp-product-name">{product_subtitle}</div>'
        '</div>'
        '<div class="gcp-header-right">'
        '<div class="gcp-date-time">'
        f'<div class="gcp-date">{escape(date_text)}</div>'
        '<div class="gcp-time">'
        f'{escape(time_text)}'
        f'<span class="gcp-tz">{escape(timezone_abbr)}</span>'
        '</div></div>'
        '<div class="gcp-user">'
        '<div class="gcp-avatar">FD</div>'
        '<div class="gcp-user-info">'
        f'<div class="gcp-hotel">{hotel_name}</div>'
        '<div class="gcp-username">FD001</div>'
        '</div></div></div></div>'
    )

    st.markdown(header_html, unsafe_allow_html=True)
    _render_sidebar_toggle_script()
