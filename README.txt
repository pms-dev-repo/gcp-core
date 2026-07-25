GCP - Single PDF Button Update

Replace:
- components/workflow.py
- services/document_service.py

Add to requirements.txt:
docx2pdf>=0.1.8

New PDF behavior:
- Only one PDF button is displayed: Open Final PDF.
- Clicking it converts the edited DOCX to PDF using Microsoft Word.
- The generated PDF opens in a new browser tab.
- The original Word formatting is preserved.

Requirements:
- Run Streamlit locally on Windows.
- Microsoft Word must be installed.
- Save the edited DOCX in Word before clicking Open Final PDF.
