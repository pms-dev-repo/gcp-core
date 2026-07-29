GUEST TRANSPORTATION MODULE

Copy these files into the same paths in your project:

app.py
core/module_registry.py
modules/dashboard/page.py
modules/guest_transportation/__init__.py
modules/guest_transportation/page.py
utils/state.py
config/clients/GCPHOTEL.json

This first demo version:
- Uses the existing transport data inside guests.json.
- Provides daily filters, KPIs, operational list and editable transfer workflow.
- Lets you assign driver, vehicle, pickup location, destination and status.
- Stores edits in Streamlit session_state for the demo.

Important:
Edits remain available during the current browser session only.
The next phase should store transportation records in Supabase so they persist
after refreshes, redeployments and across multiple users.
