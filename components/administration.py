from __future__ import annotations

from typing import Any

import streamlit as st


DEMO_USERS: list[dict[str, Any]] = [
    {
        "id": "demo_it_support",
        "name": "Hugo Uzabeaga",
        "email": "hugo.uzabeaga@lovocraft.net",
        "role": "IT Support",
        "status": "Active",
        "language": "English",
        "last_login": "Today, 09:18 PM",
        "permissions": [
            "Guest Mailing",
            "Generate Letters",
            "Generate PDFs",
            "Send Emails",
            "Communication History",
            "Administration",
            "Manage Users",
            "Technical Settings",
        ],
    },
    {
        "id": "demo_front_desk",
        "name": "Sarah Thompson",
        "email": "sarah.thompson@sandylane.com",
        "role": "Front Desk",
        "status": "Active",
        "language": "English",
        "last_login": "Today, 06:42 PM",
        "permissions": [
            "Guest Mailing",
            "Generate Letters",
            "Generate PDFs",
            "Send Emails",
            "Communication History",
        ],
    },
    {
        "id": "demo_general_manager",
        "name": "Michael Roberts",
        "email": "michael.roberts@sandylane.com",
        "role": "General Manager",
        "status": "Active",
        "language": "English",
        "last_login": "Yesterday, 04:15 PM",
        "permissions": [
            "Dashboard",
            "Guest Mailing",
            "Generate Letters",
            "Generate PDFs",
            "Send Emails",
            "Communication History",
            "Administration",
            "Reports",
        ],
    },
]


def _show_demo_notice(action: str) -> None:
    st.info(
        f"{action} is included in the product roadmap. "
        "This demo does not create or modify real users."
    )


def _initialize_admin_state() -> None:
    if "admin_selected_user_id" not in st.session_state:
        st.session_state.admin_selected_user_id = DEMO_USERS[0]["id"]


def _get_selected_user() -> dict[str, Any]:
    selected_id = st.session_state.get(
        "admin_selected_user_id",
        DEMO_USERS[0]["id"],
    )
    return next(
        (
            user
            for user in DEMO_USERS
            if user["id"] == selected_id
        ),
        DEMO_USERS[0],
    )


def _render_header() -> None:
    title_col, action_col = st.columns([0.76, 0.24], gap="large")

    with title_col:
        st.markdown(
            """
            <div style="margin-bottom:18px">
                <div style="
                    font-size:28px;
                    font-weight:700;
                    color:#1f2937;
                    line-height:1.2;
                ">
                    Administration
                </div>
                <div style="
                    color:#6b7280;
                    font-size:14px;
                    margin-top:5px;
                ">
                    Manage platform users, roles and access permissions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button(
            "+ New User",
            key="admin_new_user",
            type="primary",
            use_container_width=True,
        ):
            _show_demo_notice("New User")


def _render_metrics() -> None:
    total_users = len(DEMO_USERS)
    active_users = sum(
        1 for user in DEMO_USERS if user["status"] == "Active"
    )
    total_roles = len({user["role"] for user in DEMO_USERS})

    col1, col2, col3, col4 = st.columns(4, gap="small")
    col1.metric("Total Users", total_users)
    col2.metric("Active Users", active_users)
    col3.metric("Roles", total_roles)
    col4.metric("License", "Enterprise")


def _render_user_list() -> None:
    st.markdown(
        """
        <div style="
            font-size:18px;
            font-weight:650;
            margin-bottom:10px;
            color:#1f2937;
        ">
            Users
        </div>
        """,
        unsafe_allow_html=True,
    )

    header = st.columns([2.2, 1.6, 1.0, 1.4], gap="small")
    for column, label in zip(
        header,
        ["Name", "Role", "Status", "Last Login"],
    ):
        column.markdown(f"**{label}**")

    st.divider()

    for user in DEMO_USERS:
        selected = (
            st.session_state.admin_selected_user_id == user["id"]
        )
        row = st.columns([2.2, 1.6, 1.0, 1.4], gap="small")

        with row[0]:
            if st.button(
                user["name"],
                key=f"admin_select_{user['id']}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.admin_selected_user_id = user["id"]
                st.rerun()

        row[1].write(user["role"])
        row[2].write("● Active")
        row[3].write(user["last_login"].split(",")[0])

        st.markdown(
            "<hr style='margin:0.35rem 0;border:none;"
            "border-top:1px solid #eceff3;'>",
            unsafe_allow_html=True,
        )


def _render_user_details(user: dict[str, Any]) -> None:
    initials = "".join(
        part[0].upper()
        for part in user["name"].split()
        if part
    )[:2]

    user_card_html = (
        '<div style="border:1px solid #dfe3ea;border-radius:14px;'
        'background:#ffffff;padding:20px;">'
        '<div style="display:flex;align-items:center;gap:14px;'
        'margin-bottom:18px;">'
        '<div style="width:48px;height:48px;border-radius:50%;'
        'display:flex;align-items:center;justify-content:center;'
        'background:#eef1f5;color:#2f3a4a;font-weight:700;'
        f'font-size:16px;">{initials}</div>'
        '<div>'
        f'<div style="font-size:17px;font-weight:700;color:#1f2937;">'
        f'{user["name"]}</div>'
        f'<div style="color:#6b7280;font-size:13px;">'
        f'{user["role"]}</div>'
        '</div>'
        '</div>'
        '<div style="font-size:14px;font-weight:650;color:#1f2937;'
        'margin-bottom:10px;">User Details</div>'
        '<div style="font-size:13px;color:#6b7280;margin-bottom:5px;">'
        'Email</div>'
        f'<div style="font-size:14px;margin-bottom:13px;">'
        f'{user["email"]}</div>'
        '<div style="font-size:13px;color:#6b7280;margin-bottom:5px;">'
        'Role</div>'
        f'<div style="font-size:14px;margin-bottom:13px;">'
        f'{user["role"]}</div>'
        '<div style="font-size:13px;color:#6b7280;margin-bottom:5px;">'
        'Status</div>'
        '<div style="font-size:14px;margin-bottom:13px;">'
        '<span style="display:inline-block;padding:3px 9px;'
        'border-radius:999px;background:#e8f7ee;color:#177245;'
        f'font-weight:600;">● {user["status"]}</span>'
        '</div>'
        '<div style="font-size:13px;color:#6b7280;margin-bottom:5px;">'
        'Language</div>'
        f'<div style="font-size:14px;margin-bottom:13px;">'
        f'{user["language"]}</div>'
        '<div style="font-size:13px;color:#6b7280;margin-bottom:5px;">'
        'Last Login</div>'
        f'<div style="font-size:14px;">{user["last_login"]}</div>'
        '</div>'
    )

    # st.html renders HTML directly and avoids Markdown treating nested,
    # indented tags as a code block.
    st.html(user_card_html)

    st.markdown("#### Permissions")
    for permission in user["permissions"]:
        st.checkbox(
            permission,
            value=True,
            disabled=True,
            key=f"permission_{user['id']}_{permission}",
        )

    action1, action2 = st.columns(2, gap="small")
    with action1:
        if st.button(
            "Edit User",
            key=f"admin_edit_{user['id']}",
            use_container_width=True,
        ):
            _show_demo_notice("Edit User")

        if st.button(
            "Deactivate",
            key=f"admin_deactivate_{user['id']}",
            use_container_width=True,
        ):
            _show_demo_notice("Deactivate User")

    with action2:
        if st.button(
            "Reset Password",
            key=f"admin_reset_{user['id']}",
            use_container_width=True,
        ):
            _show_demo_notice("Reset Password")

        if st.button(
            "Delete User",
            key=f"admin_delete_{user['id']}",
            use_container_width=True,
        ):
            _show_demo_notice("Delete User")


def render_administration() -> None:
    _initialize_admin_state()
    _render_header()
    _render_metrics()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    list_col, details_col = st.columns([0.64, 0.36], gap="large")

    with list_col:
        _render_user_list()

    with details_col:
        _render_user_details(_get_selected_user())

    st.caption(
        "Demo module only. User creation, authentication and persistence "
        "will be connected in a future development phase."
    )
