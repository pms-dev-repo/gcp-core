GCP Sidebar Submenu v1.10

Replace:
components/sidebar.py

Included changes:
- Guest Letters is now a parent menu.
- Arrivals and Departures appears as an indented submenu.
- Existing active_page='communications' is preserved.
- Future modules are controlled by True/False flags:
  Birthdays, Anniversaries, VIP Guests, Special Events,
  Room Ready and Room Upgrades.

Example:
SHOW_BIRTHDAYS = True

Note:
Showing a future item only adds it to the sidebar. Its page route
must be added to app.py when that module is developed.
