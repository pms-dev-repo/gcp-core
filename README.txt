GCP Bulk PDF Download v1.5

Included
--------
components/workspace.py

Changes
-------
- Adds a Download PDF button for each guest with a generated PDF.
- Adds Download All PDFs to create one ZIP containing every available PDF.
- Keeps document generation, PDF generation, email sending, and clear selection unchanged.
- Guests without a generated PDF show a disabled Not Ready button.

Installation
------------
1. Replace components/workspace.py.
2. Commit and push the change.
3. Reboot the Streamlit app if needed.

No new Python package is required.
