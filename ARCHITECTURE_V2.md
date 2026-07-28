# GCP Modular Architecture v2

## Client configuration

The active hotel is selected with the `GCP_CLIENT` environment variable.
Without this variable, GCP loads `config/clients/default.json`.

Example on Windows PowerShell:

```powershell
$env:GCP_CLIENT="default"
streamlit run app.py
```

To create another hotel, copy `config/clients/default.json` to a new file such
as `config/clients/new_hotel.json`, adjust branding and module flags, then run:

```powershell
$env:GCP_CLIENT="new_hotel"
streamlit run app.py
```

## Module flags

Each module can be enabled or disabled inside the client's JSON file:

- `communications`
- `confirmation_letters`
- `registration_cards`
- `templates`
- `administration`
- `dashboard`
- `history`
- `settings`
- `about`

## Structure

- `core/`: configuration and module registry.
- `modules/`: independent product modules and pages.
- `components/`: reusable existing Streamlit components.
- `services/`: document, email, Word and workflow services.
- `config/clients/`: per-hotel configuration.
- `templates/`: document templates.
- `data/`: demo or provider data.

## Current scope

The existing Arrivals and Departures workflow remains operational.
Confirmation Letters and Registration Cards are enabled as module shells ready
for their document templates and specific data mappings.
