"""Document extraction helpers that preserve PDF page boundaries and line breaks."""
from pathlib import Path
from docx import Document as DocxDocument
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

class DocumentProcessingError(Exception):
    pass

def validate_file_type(file_path: str | Path) -> bool:
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS

def clean_text(text: str) -> str:
    """Normalize whitespace while preserving blank lines and line boundaries."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    # Keep one blank line between paragraphs; don't collapse the page to one line.
    out = []
    blank = False
    for line in lines:
        if line:
            out.append(line)
            blank = False
        elif out and not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()

def extract_document_pages(file_path: str | Path) -> list[dict]:
    path = Path(file_path)
    if not path.exists():
        raise DocumentProcessingError(f"File does not exist: {path}")
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise DocumentProcessingError(f"Unsupported file type: {ext}")
    try:
        if ext == ".pdf":
            reader = PdfReader(str(path))
            units = [{"page_number": i, "text": clean_text(page.extract_text() or "")}
                     for i, page in enumerate(reader.pages, start=1)]
        elif ext == ".docx":
            doc = DocxDocument(str(path))
            text = clean_text("\n\n".join(p.text for p in doc.paragraphs))
            units = [{"page_number": None, "text": text}]
        else:
            text = clean_text(path.read_text(encoding="utf-8", errors="replace"))
            units = [{"page_number": None, "text": text}]
    except Exception as exc:
        raise DocumentProcessingError(f"Failed to extract text from {path.name}: {exc}") from exc
    units = [u for u in units if u["text"]]
    if not units:
        raise DocumentProcessingError(f"No readable text extracted from {path.name}")
    return units

def extract_text_from_pdf(file_path: str | Path) -> str:
    return "\n\n".join(unit["text"] for unit in extract_document_pages(file_path))

def extract_text_from_docx(file_path: str | Path) -> str:
    return extract_document_pages(file_path)[0]["text"]

def extract_text_from_txt(file_path: str | Path) -> str:
    return extract_document_pages(file_path)[0]["text"]

def extract_text(file_path: str | Path) -> str:
    return "\n\n".join(unit["text"] for unit in extract_document_pages(file_path))
