from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


def render_header() -> None:
    barbados_now = datetime.now(ZoneInfo("America/Barbados"))

    date_text = barbados_now.strftime("%A, %d %b, %Y")
    time_text = barbados_now.strftime("%I:%M %p")

    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            display: none;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 0 !important;
        }

        .gcp-header {
            width: 100%;
            height: 44px;
            box-sizing: border-box;
            background-color: #30364C;
            color: #FFFFFF;
            padding: 0 16px;
            margin: 0 0 14px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: "Segoe UI", Arial, sans-serif;
            overflow: hidden;
        }

        .gcp-header-left {
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }

        .gcp-brand {
            color: #FFFFFF;
            font-size: 19px;
            font-weight: 700;
            line-height: 1;
            letter-spacing: 0.7px;
            white-space: nowrap;
        }

        .gcp-divider {
            width: 1px;
            height: 20px;
            background-color: rgba(255,255,255,0.35);
            flex-shrink: 0;
        }

        .gcp-product-name {
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 400;
            white-space: nowrap;
        }

        .gcp-header-right {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 17px;
            margin-left: auto;
            height: 100%;
        }

        .gcp-date-time {
            color: #FFFFFF;
            text-align: right;
            line-height: 1.15;
            white-space: nowrap;
        }

        .gcp-date {
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 600;
        }

        .gcp-time {
            color: #D9DCE6;
            font-size: 9px;
            margin-top: 2px;
        }

        .gcp-user {
            display: flex;
            align-items: center;
            gap: 9px;
            height: 100%;
        }

        .gcp-avatar {
            width: 26px;
            height: 26px;
            border-radius: 6px;
            background-color: #69728F;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            font-weight: 600;
            flex-shrink: 0;
        }

        .gcp-user-info {
            display: flex;
            flex-direction: column;
            justify-content: center;
            line-height: 1.12;
            white-space: nowrap;
        }

        .gcp-hotel {
            color: #FFFFFF;
            font-size: 9px;
            font-weight: 600;
        }

        .gcp-username {
            color: #FFFFFF;
            font-size: 9px;
            font-weight: 500;
            margin-top: 2px;
        }

        @media (max-width: 800px) {
            .gcp-product-name,
            .gcp-hotel,
            .gcp-time {
                display: none;
            }

            .gcp-header {
                padding: 0 10px;
            }

            .gcp-header-right {
                gap: 9px;
            }

            .gcp-date {
                font-size: 9px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Importante: HTML continuo, sin líneas vacías ni indentación Markdown.
    header_html = (
        '<div class="gcp-header">'
        '<div class="gcp-header-left">'
        '<div class="gcp-brand">GCP</div>'
        '<div class="gcp-divider"></div>'
        '<div class="gcp-product-name">Guest Communication Platform</div>'
        '</div>'
        '<div class="gcp-header-right">'
        '<div class="gcp-date-time">'
        f'<div class="gcp-date">{date_text}</div>'
        f'<div class="gcp-time">{time_text} AST</div>'
        '</div>'
        '<div class="gcp-user">'
        '<div class="gcp-avatar">FD</div>'
        '<div class="gcp-user-info">'
        '<div class="gcp-hotel">SANDY LANE</div>'
        '<div class="gcp-username">FD001</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(header_html, unsafe_allow_html=True)