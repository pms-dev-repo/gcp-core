from __future__ import annotations

import streamlit as st


def render_module_placeholder(
    title: str,
    description: str,
    next_steps: tuple[str, ...] = (),
) -> None:
    items = "".join(f"<li>{item}</li>" for item in next_steps)
    checklist = f"<ul>{items}</ul>" if items else ""
    st.markdown(
        f"""
        <div class="empty-workspace-card">
            <div class="empty-workspace-icon">▤</div>
            <div class="empty-workspace-title">{title}</div>
            <div class="empty-workspace-text">{description}</div>
            {checklist}
        </div>
        """,
        unsafe_allow_html=True,
    )
