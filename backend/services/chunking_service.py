"""Page- and section-aware chunking that preserves headings with their content."""
import re

# Policy headings typically look like "8. Disciplinary Action" or "3.1 Passwords".
_HEADING = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2})*)\.?\s+([A-Z][^\n]{1,130})\s*$")

class ChunkingService:
    DEFAULT_CHUNK_SIZE = 1200
    DEFAULT_CHUNK_OVERLAP = 180

    def chunk_pages(self, pages: list[dict], chunk_size: int = DEFAULT_CHUNK_SIZE,
                    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[dict]:
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Require chunk_size > chunk_overlap >= 0.")
        output: list[dict] = []
        current_section = None

        for page in pages:
            page_no = page.get("page_number")
            lines = (page.get("text") or "").splitlines()
            buffer_lines: list[str] = []

            def emit(lines_to_emit: list[str]):
                text = "\n".join(lines_to_emit).strip()
                if text:
                    output.append({
                        "content": text,
                        "page_number": page_no,
                        "section_title": current_section,
                    })

            def flush():
                nonlocal buffer_lines
                if buffer_lines:
                    emit(buffer_lines)
                    buffer_lines = []

            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    # Preserve paragraph separation without letting blank runs grow.
                    if buffer_lines and buffer_lines[-1] != "":
                        buffer_lines.append("")
                    continue

                heading = _HEADING.match(line)
                if heading:
                    flush()
                    current_section = line[:180]
                    buffer_lines.append(line)
                    continue

                # Avoid treating recurring PDF page furniture as substantive content.
                if re.fullmatch(r"Page\s+\d+", line, flags=re.I):
                    continue

                # A single very long line is split at whitespace boundaries.
                if len(line) > chunk_size:
                    flush()
                    start = 0
                    while start < len(line):
                        end = min(start + chunk_size, len(line))
                        if end < len(line):
                            boundary = line.rfind(" ", start, end)
                            if boundary > start:
                                end = boundary
                        piece = line[start:end].strip()
                        if piece:
                            output.append({"content": piece, "page_number": page_no,
                                           "section_title": current_section})
                        if end >= len(line):
                            break
                        start = max(start + 1, end - chunk_overlap)
                    continue

                candidate_len = sum(len(x) for x in buffer_lines) + len(line) + len(buffer_lines)
                if buffer_lines and candidate_len > chunk_size:
                    previous = buffer_lines
                    flush()
                    # Overlap only within the same page and section; preserve complete lines.
                    overlap_lines = []
                    used = 0
                    for old_line in reversed(previous):
                        if not old_line:
                            continue
                        if used + len(old_line) > chunk_overlap:
                            break
                        overlap_lines.insert(0, old_line)
                        used += len(old_line)
                    buffer_lines = overlap_lines
                buffer_lines.append(line)

            flush()

        return output

    def chunk_text(self, text: str, chunk_size: int = DEFAULT_CHUNK_SIZE,
                   chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
        return [x["content"] for x in self.chunk_pages(
            [{"page_number": None, "text": text}], chunk_size, chunk_overlap)]

chunking_service = ChunkingService()

def chunk_text(text: str, chunk_size: int = ChunkingService.DEFAULT_CHUNK_SIZE,
               chunk_overlap: int = ChunkingService.DEFAULT_CHUNK_OVERLAP) -> list[str]:
    return chunking_service.chunk_text(text, chunk_size, chunk_overlap)
