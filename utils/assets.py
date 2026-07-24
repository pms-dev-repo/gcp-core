# utils/assets.py

from pathlib import Path
import streamlit as st


def load_svg(path: str) -> str:
    svg_path = Path(path)

    if not svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {svg_path}")

    return svg_path.read_text(encoding="utf-8")


def render_svg(
    path: str,
    width: int = 160,
    css_class: str = "gcp-logo",
) -> None:
    svg = load_svg(path)

    st.markdown(
        f"""
        <div class="{css_class}" style="width:{width}px;">
            {svg}
        </div>
        """,
        unsafe_allow_html=True,
    )