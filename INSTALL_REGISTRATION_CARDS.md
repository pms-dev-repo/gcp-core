# GCP Registration Cards Demo

Copy the files into the same relative folders in your `gcp-core` project.

Install the handwritten-signature dependency:

```bash
python -m pip install -r requirements-registration-cards.txt
```

Run GCP:

```bash
python -m streamlit run app.py
```

## Demo flow

1. Select **Accor Peru**.
2. Open **Front Office → Registration Cards**.
3. Select an arrival.
4. Generate the card. A unique number such as `RC-2026-000001` is assigned.
5. Send the demo email.
6. Open the guest form.
7. Complete the fields and draw the signature.
8. Submit. The GCP status changes to **Signed**.

## Local demo URL

The public guest link uses:

`http://localhost:8501/?registration_token=...`

For a real remote demo, update `registration_cards.public_base_url`
inside `config/clients/accor.json` to the deployed HTTPS URL.

## Important

The JSON store is suitable for a local demo only. A production deployment
should store cards, tokens, responses, and signatures in a database such as
Supabase/PostgreSQL and use proper authentication, encryption, retention,
and audit controls.
