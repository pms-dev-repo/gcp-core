import streamlit as st


def render_header() -> None:
    st.markdown(
        """
        <div class="top-header">
          <div>
            <h1>Communication Center</h1>
            <p>Select a guest, prepare the document in Word 365, and send it by email.</p>
          </div>
          <div class="hotel-name">🔔 Sandy Lane ▼ &nbsp; HU</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
