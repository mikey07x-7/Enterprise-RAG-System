"""
Document Upload / Processing Utilities

Handles:
- File type validation
- PDF text extraction
- DOCX text extraction
- TXT / Markdown text extraction
- Text cleaning
"""

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


# ==========================================================
# Processing Exception
# ==========================================================

class DocumentProcessingError(Exception):
    """Raised when document processing fails."""


# ==========================================================
# File Validation
# ==========================================================

def validate_file_type(
    file_path: str | Path,
) -> bool:
    """
    Check whether the file has a supported extension.
    """

    extension = Path(file_path).suffix.lower()

    return extension in SUPPORTED_EXTENSIONS


# ==========================================================
# PDF Extraction
# ==========================================================

def extract_text_from_pdf(
    file_path: str | Path,
) -> str:
    """
    Extract text from a PDF file.
    """

    try:
        reader = PdfReader(str(file_path))

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    except Exception as exc:

        raise DocumentProcessingError(
            f"Failed to extract text from PDF: {exc}"
        ) from exc


# ==========================================================
# DOCX Extraction
# ==========================================================

def extract_text_from_docx(
    file_path: str | Path,
) -> str:
    """
    Extract text from a DOCX file.
    """

    try:
        document = DocxDocument(
            str(file_path)
        )

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n\n".join(paragraphs)

    except Exception as exc:

        raise DocumentProcessingError(
            f"Failed to extract text from DOCX: {exc}"
        ) from exc


# ==========================================================
# TXT / Markdown Extraction
# ==========================================================

def extract_text_from_txt(
    file_path: str | Path,
) -> str:
    """
    Extract text from TXT or Markdown files.
    """

    try:

        return Path(file_path).read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception as exc:

        raise DocumentProcessingError(
            f"Failed to read text file: {exc}"
        ) from exc


# ==========================================================
# Text Cleaning
# ==========================================================

def clean_text(
    text: str,
) -> str:
    """
    Clean extracted document text.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    lines = []

    for line in text.split("\n"):

        line = " ".join(
            line.split()
        )

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


# ==========================================================
# Main Extraction Function
# ==========================================================

def extract_text(
    file_path: str | Path,
) -> str:
    """
    Extract and clean text from a supported document.
    """

    path = Path(file_path)

    if not path.exists():

        raise DocumentProcessingError(
            f"File does not exist: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise DocumentProcessingError(
            f"Unsupported file type: {extension}"
        )

    # ------------------------------------------------------
    # PDF
    # ------------------------------------------------------

    if extension == ".pdf":

        text = extract_text_from_pdf(
            path
        )

    # ------------------------------------------------------
    # DOCX
    # ------------------------------------------------------

    elif extension == ".docx":

        text = extract_text_from_docx(
            path
        )

    # ------------------------------------------------------
    # TXT / MD
    # ------------------------------------------------------

    elif extension in {
        ".txt",
        ".md",
    }:

        text = extract_text_from_txt(
            path
        )

    else:

        raise DocumentProcessingError(
            f"Unsupported file type: {extension}"
        )

    # ------------------------------------------------------
    # Clean
    # ------------------------------------------------------

    cleaned_text = clean_text(
        text
    )

    if not cleaned_text:

        raise DocumentProcessingError(
            "No readable text was extracted "
            "from the document."
        )

    return cleaned_text