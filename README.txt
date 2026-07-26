GCP Administration Demo v1.6

Included files
--------------
app.py
components/administration.py
components/sidebar.py
utils/state.py

What this version adds
----------------------
- Administration item remains visible under MANAGEMENT.
- Real Administration demo page instead of the generic placeholder.
- Three demo roles:
  - IT Support
  - Front Desk
  - General Manager
- User metrics, user list, user detail panel and visual permissions.
- New User, Edit User, Reset Password, Deactivate and Delete actions.
- All actions are demo-only and do not create, update or delete real users.

Installation
------------
1. Replace app.py.
2. Add components/administration.py.
3. Replace components/sidebar.py and utils/state.py only if your current
   copies still match the files originally supplied for this version.
4. Commit and push.
5. Reboot the Streamlit app if required.

No new dependencies are required.
