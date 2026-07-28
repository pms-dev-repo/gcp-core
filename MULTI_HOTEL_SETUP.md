# GCP Multi-Hotel Setup

Run the application normally:

```powershell
streamlit run app.py
```

The hotel selector appears at the top of the sidebar. The included demo clients are:

- Sandy Lane
- Accor Hotels

## Add another hotel

1. Copy `config/clients/sandy_lane.json` and rename it with the new client code.
2. Create `data/<client_code>/guests.json`.
3. Create `templates/<client_code>/` and add the DOCX templates.
4. Restart Streamlit only when adding a brand-new JSON file. Switching existing hotels does not require restarting.

Generated files are isolated under `generated/<client_code>/`.
