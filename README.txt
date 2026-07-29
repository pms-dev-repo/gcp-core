GCP Flight Center — Batch 1

1. Run sql/001_openflights.sql in Supabase SQL Editor.
2. Copy each file into the matching project folder.
3. Install/update dependencies:
   pip install -r requirements.txt
4. Synchronize OpenFlights:
   python -m scripts.sync_openflights
5. Add the page routing in app.py so active_page == "flight_center"
   imports and calls modules.flight_center.page.render.

Important:
- OpenFlights identifies airlines, airports and historical routes.
- GCP assembles values such as BA + 254 = BA254.
- OpenFlights does not validate that BA254 is a current scheduled service.
