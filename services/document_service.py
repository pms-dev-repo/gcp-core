from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from docx import Document


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "generated"


def _replace_tokens_in_paragraph(paragraph, replacements: dict[str, str]) -> None:
    """Replace placeholders even when Word splits them across several runs.

    The paragraph's existing run formatting is preserved as much as possible:
    replacement text is written into the first affected run and the remaining
    affected runs are cleared.
    """
    if not paragraph.runs:
        return

    full_text = "".join(run.text for run in paragraph.runs)
    if not any(token in full_text for token in replacements):
        return

    updated_text = full_text
    for token, value in replacements.items():
        updated_text = updated_text.replace(token, value)

    # Put the final text in the first run so placeholders split by Word are
    # still replaced. The first run keeps the paragraph's principal style.
    paragraph.runs[0].text = updated_text
    for run in paragraph.runs[1:]:
        run.text = ""


def _replace_tokens_in_table(table, replacements: dict[str, str]) -> None:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                _replace_tokens_in_paragraph(paragraph, replacements)
            for nested_table in cell.tables:
                _replace_tokens_in_table(nested_table, replacements)


def _replace_tokens_in_headers_and_footers(document, replacements: dict[str, str]) -> None:
    for section in document.sections:
        for area in (section.header, section.footer):
            for paragraph in area.paragraphs:
                _replace_tokens_in_paragraph(paragraph, replacements)
            for table in area.tables:
                _replace_tokens_in_table(table, replacements)


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned.strip("_") or "guest"


def _resolve_template(guest: dict[str, Any]) -> tuple[Path, str]:
    movement = str(guest.get("movement", "")).strip().lower()
    template = guest.get("template", {})
    configured_name = str(template.get("file_name", "")).strip()

    if movement == "arrivals":
        default_name = "arrival_standard_en.docx"
        default_prefix = "ARRIVAL"
    elif movement == "departures":
        default_name = "departure_standard_en.docx"
        default_prefix = "DEPARTURE"
    else:
        raise ValueError(f"Unsupported movement: {guest.get('movement')}")

    template_name = configured_name or default_name
    template_path = TEMPLATES_DIR / template_name

    # Demo fallback: if a configured language template is not present, use the
    # standard English template for the same movement.
    if not template_path.exists():
        fallback_path = TEMPLATES_DIR / default_name
        if fallback_path.exists():
            template_path = fallback_path
        else:
            raise FileNotFoundError(
                f"Template not found: {template_path}. "
                f"Fallback also not found: {fallback_path}"
            )

    prefix = str(template.get("document_prefix") or default_prefix).upper()
    return template_path, prefix


def generate_guest_document(guest: dict[str, Any]) -> Path:
    template_path, document_prefix = _resolve_template(guest)

    stay = guest.get("stay", {})
    transport = guest.get("transport", {})
    letter_date = guest.get("letter_date") or datetime.now().strftime("%d %B %Y")

    replacements = {
        "{{letter_date}}": str(letter_date),
        "{{salutation}}": str(guest.get("salutation") or ""),
        "{{guest_full_name}}": str(guest.get("full_name") or ""),
        "{{guest_first_name}}": str(guest.get("first_name") or ""),
        "{{guest_last_name}}": str(guest.get("last_name") or ""),
        "{{room_number}}": str(guest.get("room") or "To be assigned"),
        "{{arrival_date}}": str(stay.get("arrival_date") or "To be confirmed"),
        "{{departure_date}}": str(stay.get("departure_date") or "To be confirmed"),
        "{{eta}}": str(transport.get("eta") or "To be confirmed"),
        "{{confirmation_number}}": str(guest.get("confirmation_number") or ""),
        "{{email}}": str(guest.get("email") or ""),
    }

    document = Document(template_path)

    for paragraph in document.paragraphs:
        _replace_tokens_in_paragraph(paragraph, replacements)
    for table in document.tables:
        _replace_tokens_in_table(table, replacements)
    _replace_tokens_in_headers_and_footers(document, replacements)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_filename(str(guest.get("full_name") or "guest"))
    confirmation = _safe_filename(str(guest.get("confirmation_number") or "no_confirmation"))
    filename = f"{document_prefix}_{confirmation}_{safe_name}.docx"

    output_path = GENERATED_DIR / filename
    document.save(output_path)
    return output_path


def read_generated_document(path_value: str | Path) -> bytes:
    path = Path(path_value)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Generated document not found: {path}")
    return path.read_bytes()


def generate_guest_pdf(docx_path_value: str | Path) -> Path:
    """
    Convert the edited DOCX to PDF using Microsoft Word.

    This preserves the Word document layout, fonts, images, headers, footers,
    tables, and other formatting. It is intended for local Windows execution
    where Microsoft Word is installed.
    """
    try:
        from docx2pdf import convert
    except ImportError as exc:
        raise RuntimeError(
            "PDF generation requires docx2pdf. "
            "Install it with: pip install docx2pdf"
        ) from exc

    docx_path = Path(docx_path_value).resolve()

    if not docx_path.exists() or not docx_path.is_file():
        raise FileNotFoundError(
            f"Generated Word document not found: {docx_path}"
        )

    if docx_path.suffix.lower() != ".docx":
        raise ValueError("Only DOCX files can be converted to PDF.")

    pdf_path = docx_path.with_suffix(".pdf")

    try:
        convert(str(docx_path), str(pdf_path))
    except Exception as exc:
        raise OSError(
            "Microsoft Word could not convert the document to PDF. "
            "Confirm that Word is installed and that the DOCX is not open "
            "with unsaved changes."
        ) from exc

    if not pdf_path.exists():
        raise OSError("The PDF file was not created.")

    return pdf_path


def open_pdf_in_new_tab(pdf_path_value: str | Path) -> None:
    """
    Open a local PDF in the user's default browser.

    This works when Streamlit is running locally on the same computer as the
    browser, which is the current GCP demo setup.
    """
    import webbrowser

    pdf_path = Path(pdf_path_value).resolve()

    if not pdf_path.exists() or not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    opened = webbrowser.open_new_tab(pdf_path.as_uri())
    if not opened:
        raise OSError("The browser could not open the PDF in a new tab.")
