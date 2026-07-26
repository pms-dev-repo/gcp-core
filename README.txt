GCP PDF Viewer v1.4

Included files
--------------
components/document_panel.py
requirements.txt

What changed
------------
- Replaced the HTML/base64 iframe PDF preview.
- Added streamlit-pdf-viewer for Streamlit Cloud compatibility.
- Keeps the PDF download and email workflow unchanged.
- Works with the multiplatform PDF conversion engine from v1.2.
- Works with the individual workflow from v1.3.

Install
-------
1. Replace components/document_panel.py.
2. Replace or merge requirements.txt.
3. Commit and push.
4. Reboot the Streamlit Community Cloud app.

Important
---------
Keep packages.txt from v1.2 with:

libreoffice
