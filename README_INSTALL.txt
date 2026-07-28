FILES TO REPLACE

modules/confirmation_letters/page.py
services/guest_service.py
services/document_service.py
services/email_service.py
data/accor/guests.json

The document service first looks for confirmation_standard_en.docx and cancellation_standard_en.docx.
If they do not exist, it uses arrival_standard_en.docx and departure_standard_en.docx as temporary fallbacks.

The generated/sent state is kept in Streamlit session_state for this first test version.
