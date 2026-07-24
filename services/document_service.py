from __future__ import annotations

import io
from typing import Any

from docx import Document


def build_docx(guest: dict[str, Any]) -> bytes:
    document = Document()
    document.add_heading(guest["template"]["name"], level=1)
    document.add_paragraph(f"Dear {guest['first_name']} {guest['last_name']},")
    document.add_paragraph(
        f"Welcome to Sandy Lane. We are delighted to welcome you on "
        f"{guest['stay']['arrival_date']}. Your room is {guest['room']} and "
        f"your expected arrival time is {guest['transport']['eta']}."
    )
    document.add_paragraph(
        "Our Guest Relations team remains available should you require any assistance."
    )
    document.add_paragraph("Warm regards,\nGuest Relations\nSandy Lane")
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
