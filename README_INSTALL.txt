Replace services/registration_card_service.py.

In app.py add the snippet from APP_PATCH.txt immediately after st.set_page_config().

Links will include:
?client=accor&registration_token=...

The app will load the correct hotel before validating the token.
