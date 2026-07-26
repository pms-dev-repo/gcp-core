from __future__ import annotations

from typing import Any

import streamlit as st


DEMO_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "arrival_welcome",
        "name": "Arrival Welcome Letter",
        "category": "Arrival",
        "event_type": "Guest Arrival",
        "language": "English",
        "status": "Active",
        "subject": "Welcome to Sandy Lane",
        "updated": "Today",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "Welcome to {{hotel_name}}. We are delighted to welcome you on "
            "{{arrival_date}}.\n\n"
            "Your room is {{room_number}} and your confirmation number is "
            "{{confirmation_number}}.\n\n"
            "Warm regards,\nGuest Relations"
        ),
    },
    {
        "id": "departure_letter",
        "name": "Departure Letter",
        "category": "Departure",
        "event_type": "Guest Departure",
        "language": "English",
        "status": "Active",
        "subject": "Thank you for staying with us",
        "updated": "Yesterday",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "We hope you have enjoyed your stay at {{hotel_name}}.\n\n"
            "Please note that checkout time is 12:00 PM unless otherwise "
            "confirmed.\n\n"
            "Yours sincerely,\nDuty Manager"
        ),
    },
    {
        "id": "birthday_greeting",
        "name": "Birthday Greeting",
        "category": "Celebration",
        "event_type": "Birthday",
        "language": "English",
        "status": "Active",
        "subject": "Happy Birthday from Sandy Lane",
        "updated": "Jul 24",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "On behalf of everyone at {{hotel_name}}, we would like to wish "
            "you a very happy birthday.\n\n"
            "We hope you enjoy this special day with us.\n\n"
            "Warm regards,\nGuest Relations"
        ),
    },
    {
        "id": "anniversary_greeting",
        "name": "Anniversary Greeting",
        "category": "Celebration",
        "event_type": "Anniversary",
        "language": "English",
        "status": "Draft",
        "subject": "Warm Anniversary Wishes",
        "updated": "Jul 22",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "Congratulations on your anniversary. It is a pleasure to share "
            "this special occasion with you at {{hotel_name}}.\n\n"
            "Warm regards,\nGuest Relations"
        ),
    },
    {
        "id": "vip_welcome",
        "name": "VIP Welcome Letter",
        "category": "VIP",
        "event_type": "VIP Arrival",
        "language": "English",
        "status": "Active",
        "subject": "A Special Welcome to Sandy Lane",
        "updated": "Jul 20",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "It is our pleasure to welcome you to {{hotel_name}} as our valued "
            "VIP guest.\n\n"
            "Our team remains available throughout your stay.\n\n"
            "Warm regards,\nGeneral Manager"
        ),
    },
    {
        "id": "special_event",
        "name": "Special Event Invitation",
        "category": "Events",
        "event_type": "Special Event",
        "language": "English",
        "status": "Active",
        "subject": "You Are Invited",
        "updated": "Jul 18",
        "content": (
            "Dear {{salutation}} {{guest_name}},\n\n"
            "We are pleased to invite you to {{event_name}} on {{event_date}} "
            "at {{event_time}}.\n\n"
            "Location: {{event_location}}\n\n"
            "Warm regards,\nGuest Relations"
        ),
    },
]

AVAILABLE_VARIABLES = [
    "{{guest_name}}",
    "{{salutation}}",
    "{{room_number}}",
    "{{confirmation_number}}",
    "{{arrival_date}}",
    "{{departure_date}}",
    "{{hotel_name}}",
    "{{birthday_date}}",
    "{{anniversary_date}}",
    "{{event_name}}",
    "{{event_date}}",
    "{{event_time}}",
    "{{event_location}}",
]


def _initialize_template_state() -> None:
    if "template_selected_id" not in st.session_state:
        st.session_state.template_selected_id = DEMO_TEMPLATES[0]["id"]


def _selected_template() -> dict[str, Any]:
    selected_id = st.session_state.get(
        "template_selected_id",
        DEMO_TEMPLATES[0]["id"],
    )
    return next(
        (
            template
            for template in DEMO_TEMPLATES
            if template["id"] == selected_id
        ),
        DEMO_TEMPLATES[0],
    )


def _demo_notice(action: str) -> None:
    st.info(
        f"{action} is available in the planned production version. "
        "This demo does not save or modify templates."
    )


def _render_header() -> None:
    title_col, action_col = st.columns([0.76, 0.24], gap="large")

    with title_col:
        st.markdown("## Template Studio")
        st.caption(
            "Create and manage reusable guest communication templates."
        )

    with action_col:
        if st.button(
            "+ New Template",
            key="template_new",
            type="primary",
            use_container_width=True,
        ):
            _demo_notice("New Template")


def _render_metrics() -> None:
    active = sum(
        1 for template in DEMO_TEMPLATES
        if template["status"] == "Active"
    )
    categories = len(
        {template["category"] for template in DEMO_TEMPLATES}
    )
    languages = len(
        {template["language"] for template in DEMO_TEMPLATES}
    )

    col1, col2, col3, col4 = st.columns(4, gap="small")
    col1.metric("Templates", len(DEMO_TEMPLATES))
    col2.metric("Active", active)
    col3.metric("Categories", categories)
    col4.metric("Languages", languages)


def _render_template_list() -> None:
    st.markdown("### Templates")

    search = st.text_input(
        "Search templates",
        placeholder="Search by name, category or event...",
        key="template_search",
        label_visibility="collapsed",
    ).strip().lower()

    filtered = [
        template
        for template in DEMO_TEMPLATES
        if not search
        or search in template["name"].lower()
        or search in template["category"].lower()
        or search in template["event_type"].lower()
    ]

    header = st.columns([2.3, 1.2, 1.0, 0.9], gap="small")
    for column, label in zip(
        header,
        ["Template", "Category", "Language", "Status"],
    ):
        column.markdown(f"**{label}**")

    st.divider()

    for template in filtered:
        selected = (
            st.session_state.template_selected_id == template["id"]
        )
        row = st.columns([2.3, 1.2, 1.0, 0.9], gap="small")

        with row[0]:
            if st.button(
                template["name"],
                key=f"template_select_{template['id']}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.template_selected_id = template["id"]
                st.rerun()

        row[1].write(template["category"])
        row[2].write(template["language"])
        row[3].write(
            "● Active"
            if template["status"] == "Active"
            else "○ Draft"
        )

        st.markdown(
            "<hr style='margin:0.35rem 0;border:none;"
            "border-top:1px solid #eceff3;'>",
            unsafe_allow_html=True,
        )

    if not filtered:
        st.info("No templates match your search.")


def _render_template_details(template: dict[str, Any]) -> None:
    st.markdown("### Template Details")

    detail_col1, detail_col2 = st.columns(2, gap="small")
    detail_col1.text_input(
        "Template Name",
        value=template["name"],
        disabled=True,
        key=f"template_name_{template['id']}",
    )
    detail_col2.text_input(
        "Status",
        value=template["status"],
        disabled=True,
        key=f"template_status_{template['id']}",
    )

    detail_col1.text_input(
        "Category",
        value=template["category"],
        disabled=True,
        key=f"template_category_{template['id']}",
    )
    detail_col2.text_input(
        "Event Type",
        value=template["event_type"],
        disabled=True,
        key=f"template_event_{template['id']}",
    )

    detail_col1.text_input(
        "Language",
        value=template["language"],
        disabled=True,
        key=f"template_language_{template['id']}",
    )
    detail_col2.text_input(
        "Last Updated",
        value=template["updated"],
        disabled=True,
        key=f"template_updated_{template['id']}",
    )

    st.text_input(
        "Email Subject",
        value=template["subject"],
        disabled=True,
        key=f"template_subject_{template['id']}",
    )

    st.text_area(
        "Template Content",
        value=template["content"],
        height=260,
        disabled=True,
        key=f"template_content_{template['id']}",
    )

    st.markdown("#### Available Variables")
    variable_columns = st.columns(2, gap="small")
    for index, variable in enumerate(AVAILABLE_VARIABLES):
        variable_columns[index % 2].code(variable)

    st.markdown("#### Preview")
    preview_text = (
        template["content"]
        .replace("{{salutation}}", "Dr.")
        .replace("{{guest_name}}", "Helen Young")
        .replace("{{hotel_name}}", "Sandy Lane")
        .replace("{{room_number}}", "327")
        .replace("{{confirmation_number}}", "3000011")
        .replace("{{arrival_date}}", "26 July 2026")
        .replace("{{departure_date}}", "30 July 2026")
        .replace("{{birthday_date}}", "26 July 2026")
        .replace("{{anniversary_date}}", "26 July 2026")
        .replace("{{event_name}}", "Sunset Cocktail Reception")
        .replace("{{event_date}}", "27 July 2026")
        .replace("{{event_time}}", "6:30 PM")
        .replace("{{event_location}}", "The Beach Club")
    )

    st.text_area(
        "Document Preview",
        value=preview_text,
        height=220,
        disabled=True,
        key=f"template_preview_{template['id']}",
        label_visibility="collapsed",
    )

    action1, action2, action3, action4 = st.columns(4, gap="small")

    with action1:
        if st.button(
            "Edit",
            key=f"template_edit_{template['id']}",
            use_container_width=True,
        ):
            _demo_notice("Edit Template")

    with action2:
        if st.button(
            "Duplicate",
            key=f"template_duplicate_{template['id']}",
            use_container_width=True,
        ):
            _demo_notice("Duplicate Template")

    with action3:
        action_label = (
            "Deactivate"
            if template["status"] == "Active"
            else "Activate"
        )
        if st.button(
            action_label,
            key=f"template_activate_{template['id']}",
            use_container_width=True,
        ):
            _demo_notice(action_label)

    with action4:
        if st.button(
            "Archive",
            key=f"template_archive_{template['id']}",
            use_container_width=True,
        ):
            _demo_notice("Archive Template")


def render_template_studio() -> None:
    _initialize_template_state()
    _render_header()
    _render_metrics()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    list_col, detail_col = st.columns([0.45, 0.55], gap="large")

    with list_col:
        _render_template_list()

    with detail_col:
        _render_template_details(_selected_template())

    st.caption(
        "Demo module only. Template persistence, approvals and role-based "
        "access will be connected in a future development phase."
    )
