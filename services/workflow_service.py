from __future__ import annotations

from pathlib import Path
from typing import Any

from services.document_service import generate_guest_document, generate_guest_pdf
from services.email_service import send_guest_email


class DocumentWorkflowService:
    """Application-level facade for document generation and delivery workflows."""

    def generate_docx(self, guest: dict[str, Any]) -> Path:
        return Path(generate_guest_document(guest))

    def generate_pdf(self, document_path: str | Path) -> Path:
        return Path(generate_guest_pdf(document_path))

    def send(self, guest: dict[str, Any]) -> bool:
        return bool(send_guest_email(guest))
