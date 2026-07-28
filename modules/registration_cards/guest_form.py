from __future__ import annotations

import io
from datetime import date
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from services.registration_card_service import (
    mark_card_opened,
    save_guest_response,
)

try:
    from streamlit_drawable_canvas import st_canvas
except ImportError:
    st_canvas = None


def _signature_canvas(key: str) -> bytes | None:
    if st_canvas is None:
        st.warning(
            "Install streamlit-drawable-canvas to enable handwritten "
            "signatures: pip install streamlit-drawable-canvas"
        )
        return None

    canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#111827",
        background_color="#FFFFFF",
        height=180,
        width=700,
        drawing_mode="freedraw",
        key=key,
    )

    if canvas.image_data is None:
        return None

    image = Image.fromarray(canvas.image_data.astype("uint8"), "RGBA")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _has_visible_signature(signature_png: bytes | None) -> bool:
    if not signature_png:
        return False

    image = Image.open(io.BytesIO(signature_png)).convert("RGBA")
    pixels = image.getdata()

    for red, green, blue, alpha in pixels:
        if alpha > 0 and min(red, green, blue) < 245:
            return True
    return False


def render_guest_registration_form(token: str) -> None:
    st.set_page_config(
        page_title="Online Registration Card",
        page_icon="✍️",
        layout="centered",
    )

    card = mark_card_opened(token)
    if not card:
        st.error("This registration-card link is invalid or has expired.")
        st.stop()

    guest = card.get("guest", {})

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="stHeader"]{display:none}
        .block-container{max-width:900px;padding-top:1.5rem}
        .rc-header{
            padding:22px 24px;
            border-radius:12px;
            background:#30364C;
            color:white;
            margin-bottom:20px;
        }
        .rc-number{font-size:12px;opacity:.8}
        .rc-title{font-size:24px;font-weight:750;margin-top:4px}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="rc-header">
            <div class="rc-number">
                Registration Card {card["registration_card_number"]}
            </div>
            <div class="rc-title">Complete your hotel registration</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if card.get("status") == "Signed":
        st.success(
            "Thank you. Your registration card was already completed and signed.",
            icon="✅",
        )
        st.write(
            f"Completed at: `{card.get('completed_at', '—')}`"
        )
        return

    st.info(
        "Your reservation details have been prefilled from the hotel's "
        "reservation system. Please review them and complete the missing fields."
    )

    with st.container(border=True):
        st.subheader("Reservation details")
        col1, col2 = st.columns(2)
        col1.text_input(
            "Guest name",
            value=str(guest.get("full_name") or ""),
            disabled=True,
        )
        col2.text_input(
            "Confirmation number",
            value=str(guest.get("confirmation_number") or ""),
            disabled=True,
        )
        col1.text_input(
            "Arrival",
            value=str(guest.get("arrival_date") or ""),
            disabled=True,
        )
        col2.text_input(
            "Departure",
            value=str(guest.get("departure_date") or ""),
            disabled=True,
        )
        col1.text_input(
            "Room type",
            value=str(guest.get("room_type") or ""),
            disabled=True,
        )
        col2.text_input(
            "Guests",
            value=(
                f"{guest.get('adults', 0)} adult(s), "
                f"{guest.get('children', 0)} child(ren)"
            ),
            disabled=True,
        )

    with st.form("registration_card_guest_form"):
        st.subheader("Personal information")

        col1, col2 = st.columns(2)
        phone = col1.text_input(
            "Mobile phone",
            value=str(guest.get("phone") or ""),
        )
        email = col2.text_input(
            "Email",
            value=str(guest.get("email") or ""),
        )

        document_type = col1.selectbox(
            "Document type",
            ["DNI", "Passport", "Foreign Resident Card", "Other"],
            index=0,
        )
        document_number = col2.text_input(
            "Document number",
            value=str(guest.get("document_number") or ""),
        )

        nationality = col1.text_input(
            "Nationality",
            value=str(guest.get("nationality") or ""),
        )
        birth_date = col2.date_input(
            "Date of birth",
            value=date(1990, 1, 1),
            max_value=date.today(),
        )

        address = st.text_input("Home address")
        city_col, country_col = st.columns(2)
        city = city_col.text_input("City")
        country = country_col.text_input("Country of residence")

        occupation = st.text_input("Occupation")
        emergency_contact = st.text_input(
            "Emergency contact name and phone"
        )
        special_requests = st.text_area(
            "Special requests or information for the hotel"
        )

        st.subheader("Consents")
        privacy_consent = st.checkbox(
            "I authorize the hotel to process the information provided "
            "for purposes related to my stay.",
        )
        marketing_consent = st.checkbox(
            "I would like to receive hotel news and promotional communications.",
        )

        typed_signature = st.text_input(
            "Full legal name",
            help="Enter the same name that will appear in your signature.",
        )

        st.markdown("**Draw your signature below**")
        st.caption(
            "Use your finger on a mobile device, or the mouse on a computer."
        )

        # The canvas itself must be rendered outside the form submit callback,
        # but it is still part of the visible form.
        signature_png = _signature_canvas(
            f"registration_signature_{card['registration_card_number']}"
        )

        submitted = st.form_submit_button(
            "Submit signed registration card",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        # Demo mode: all guest-entered fields, consents and signature are optional.
        response: dict[str, Any] = {
            "phone": phone.strip(),
            "email": email.strip(),
            "document_type": document_type,
            "document_number": document_number.strip(),
            "nationality": nationality.strip(),
            "birth_date": birth_date.isoformat(),
            "address": address.strip(),
            "city": city.strip(),
            "country": country.strip(),
            "occupation": occupation.strip(),
            "emergency_contact": emergency_contact.strip(),
            "special_requests": special_requests.strip(),
            "privacy_consent": privacy_consent,
            "marketing_consent": marketing_consent,
            "typed_signature": typed_signature.strip(),
        }

        save_guest_response(
            token=token,
            response=response,
            signature_png=signature_png or b"",
        )

        st.success(
            "Your registration card was submitted successfully.",
            icon="✅",
        )
        st.balloons()

        # Attempt to close the public registration tab after submission.
        # Browsers only allow window.close() automatically when the tab was
        # opened by script. If blocked, the guest sees a completion message.
        components.html(
            """
            <script>
                setTimeout(function () {
                    window.parent.close();
                    window.close();
                }, 1800);
            </script>
            """,
            height=0,
        )

        st.info(
            "Registration completed. This tab will close automatically. "
            "If your browser blocks it, you can close it now."
        )
        st.stop()
