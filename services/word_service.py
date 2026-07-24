from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def can_open_desktop_word() -> bool:
    """Return True only when the Streamlit process can open a desktop app."""
    environment = os.getenv("GCP_ENV", "auto").strip().lower()

    if environment == "cloud":
        return False
    if environment == "local":
        return platform.system() in {"Windows", "Darwin"}

    # Streamlit Community Cloud runs on Linux without a desktop session.
    return platform.system() in {"Windows", "Darwin"}


def open_in_word_365(document_path: Path) -> str:
    """Open a generated DOCX in the desktop copy of Microsoft Word."""
    document_path = Path(document_path).resolve()

    if not document_path.exists():
        raise FileNotFoundError(
            f"Generated document was not found: {document_path}"
        )

    if document_path.suffix.lower() != ".docx":
        raise ValueError("Only DOCX documents can be opened in Microsoft Word.")

    if not can_open_desktop_word():
        raise OSError(
            "Desktop Word is unavailable in this hosted environment. "
            "Download the DOCX and open it on your computer."
        )

    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(str(document_path))  # type: ignore[attr-defined]
    elif system_name == "Darwin":
        subprocess.Popen(
            ["open", "-a", "Microsoft Word", str(document_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        raise OSError(f"Unsupported desktop operating system: {system_name}")

    return document_path.as_uri()
