from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def open_in_word_365(document_path: Path) -> str:
    """
    Opens the generated DOCX in the desktop application associated with
    Microsoft Word on the computer running Streamlit.

    Important:
    - In local development, this opens Word on the same PC.
    - If Streamlit is deployed on a remote server, it opens on the server,
      not on the hotel user's computer.
    """
    document_path = Path(document_path).resolve()

    if not document_path.exists():
        raise FileNotFoundError(
            f"Generated document was not found: {document_path}"
        )

    if document_path.suffix.lower() != ".docx":
        raise ValueError("Only DOCX documents can be opened in Microsoft Word.")

    system_name = platform.system()

    if system_name == "Windows":
        # Uses the Windows default application for .docx, normally Microsoft Word.
        os.startfile(str(document_path))  # type: ignore[attr-defined]

    elif system_name == "Darwin":
        subprocess.Popen(
            ["open", "-a", "Microsoft Word", str(document_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    elif system_name == "Linux":
        subprocess.Popen(
            ["xdg-open", str(document_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    else:
        raise OSError(f"Unsupported operating system: {system_name}")

    return document_path.as_uri()
