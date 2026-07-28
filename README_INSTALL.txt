GCP - Registration Cards with Supabase
======================================

1. Copy services/database.py into your project's services folder.
2. Replace services/registration_card_service.py with the supplied file.
3. Confirm that "supabase" exists in requirements.txt.
4. Configure Streamlit Secrets using .streamlit/secrets.toml.example as a guide.
   Never commit your real secrets.toml file to GitHub.
5. Run supabase_registration_cards.sql in Supabase SQL Editor.
6. Remove the temporary Supabase connection test from app.py.
7. Deploy/restart Streamlit Cloud.
8. Generate a NEW registration card. Old links stored only in JSON will not exist
   in Supabase and will remain invalid.
9. Verify in Supabase:
   - Generated after creating the card
   - Opened after opening the public URL
   - Signed after submitting the signature form

The public functions remain compatible with the existing page.py, guest_form.py,
and email_service.py.
