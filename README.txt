GCP Bulk Communication v1.1

Replace these files in your project:
- components/workspace.py
- services/document_service.py
- services/email_service.py
- utils/state.py

Bulk flow:
1. Generate Guest Letters
2. Generate PDFs
3. Send Guest Letters

The individual workflow remains unchanged.

Important:
- PDF conversion still requires Microsoft Word and docx2pdf on Windows.
- Bulk conversion retries each failed document up to 3 times.
