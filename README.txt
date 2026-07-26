GCP Individual PDF Preview v1.3

Included files
--------------
components/workflow.py
components/document_panel.py

What changed
------------
- Removed the server-side browser opening step.
- Replaced "Open Final PDF" with "Generate & Preview PDF".
- Stores the generated PDF in session state.
- Displays the PDF inside the Streamlit application.
- Adds a "Download Final PDF" button.
- Keeps Send Email disabled until a valid PDF exists.
- Works with the multiplatform PDF engine from v1.2.

Install
-------
1. Replace components/workflow.py.
2. Replace components/document_panel.py.
3. Commit and push.
4. Reboot or rerun the Streamlit app.

No changes are required in services/document_service.py if v1.2 is already installed.
