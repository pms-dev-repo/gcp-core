# GCP Core

Single-page Streamlit demo for the **Guest Communication Platform**.

## Current demo flow

1. Select an arrival or departure.
2. Review the dynamic guest workspace.
3. Generate a DOCX.
4. Simulate opening it in Word 365.
5. Simulate sending the email.
6. Review the communication history.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

```text
app.py
components/    # Streamlit UI modules
services/      # JSON now; OHIP, Word 365 and email later
utils/         # Shared state and CSS
models/        # Reserved for typed domain models
data/          # Demo JSON only
assets/        # Logos and static assets
```

## Next integrations

- Replace `services/guest_service.py` with an OHIP adapter.
- Upload generated DOCX files to OneDrive/SharePoint through Microsoft Graph.
- Open the Microsoft Graph `webUrl` in Word for the web.
- Send messages using Microsoft Graph or the approved hotel email provider.
- Add Supabase only for GCP-owned history, templates, configuration and logs.


## Deploy to Streamlit Community Cloud

1. Push this project to the `main` branch of `pms-dev-repo/gcp-core`.
2. Open Streamlit Community Cloud and choose **Create app**.
3. Repository: `pms-dev-repo/gcp-core`
4. Branch: `main`
5. Main file path: `app.py`
6. App URL: `gcp-demo`
7. Select Python 3.12 in Advanced settings and deploy.

The hosted demo cannot launch a desktop application on the visitor's PC.
It therefore downloads the editable DOCX, which the visitor can open in
Microsoft Word. Local Windows/macOS development still opens Word Desktop.
