GCP Template Studio v1.9

Included files
--------------
app.py
components/sidebar.py
components/administration.py
components/template_management.py

What this version adds
----------------------
- New Template Studio item under MANAGEMENT.
- Template metrics and searchable template list.
- Demo templates for:
  - Arrival
  - Departure
  - Birthday
  - Anniversary
  - VIP
  - Special Events
- Template details, available variables and document preview.
- Demo actions: New, Edit, Duplicate, Activate/Deactivate and Archive.
- New role permissions:
  - Use Templates
  - Manage Templates
- IT Support and General Manager can manage templates.
- Front Desk can use templates.

Installation
------------
Replace the included files in the matching project paths.

Then restart Streamlit:
streamlit run app.py

No new dependencies are required.
