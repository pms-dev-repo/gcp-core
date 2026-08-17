from __future__ import annotations

import streamlit as st

from components.administration import render_administration
from components.header import render_header
from components.sidebar import render_sidebar
from components.template_management import render_template_studio
from core.config import (
    enabled_modules,
    get_default_client_code,
    load_client_config,
)
from modules.communications.page import render as render_communications
from modules.dashboard.page import render as render_dashboard
from modules.guest_transportation.page import render as render_guest_transportation
from modules.guest_sms.page import render as render_guest_sms
from modules.flight_center.page import render as render_flight_center
from modules.confirmation_letters.page import render as render_confirmation_letters
from modules.registration_cards.guest_form import (
    render_guest_registration_form,
)
from modules.registration_cards.page import render as render_registration_cards
from modules.reports.page import render as render_reports
from modules.shared_placeholder import render_module_placeholder
from services.guest_service import load_guests
from utils.state import initialize_state
from utils.styles import apply_global_styles

registration_token = st.query_params.get("registration_token")
if registration_token:
    render_guest_registration_form(str(registration_token))
    st.stop()


st.set_page_config(
    page_title="GCP — Guest Communication Platform",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# The active property must be resolved before loading configuration or guests.
st.session_state.setdefault(
    "active_client_code",
    get_default_client_code(),
)

client_code = str(st.session_state.active_client_code)
config = load_client_config(client_code)
active_modules = enabled_modules(config)

apply_global_styles()

guests = load_guests(client_code)
initialize_state(guests)

# Always open Dashboard on the first run of a browser session.
# A full browser refresh (F5) creates a new Streamlit session, so this
# sends the user back to Dashboard without affecting normal navigation.
if not st.session_state.get("gcp_session_initialized", False):
    st.session_state.active_page = (
        "dashboard"
        if "dashboard" in active_modules
        else next(iter(active_modules), "about")
    )
    st.session_state.gcp_session_initialized = True

# If the selected page is not enabled for the active property,
# return to Dashboard when available.
elif st.session_state.get("active_page") not in active_modules:
    st.session_state.active_page = (
        "dashboard"
        if "dashboard" in active_modules
        else next(iter(active_modules), "about")
    )

render_header()

with st.sidebar:
    render_sidebar()

active_page = st.session_state.active_page

if active_page == "dashboard":
    render_dashboard(guests)
elif active_page == "communications":
    render_communications(guests)
elif active_page == "guest_sms":
    render_guest_sms(guests)
elif active_page == "confirmation_letters":
    render_confirmation_letters()
elif active_page == "registration_cards":
    render_registration_cards()
elif active_page == "guest_transportation":
    render_guest_transportation()
elif active_page == "flight_center":
    render_flight_center()
elif active_page == "reports":
    render_reports()
elif active_page == "administration":
    render_administration()
elif active_page == "templates":
    render_template_studio()
else:
    titles = {
        "dashboard": "Dashboard",
        "history": "Document History",
        "settings": "Settings",
        "about": "About GCP",
    }
    render_module_placeholder(
        titles.get(active_page, "GCP"),
        "This module is enabled and ready for its implementation phase.",
    )
