"""
Text Chunking Service

Splits extracted document text into overlapping chunks
for embedding and semantic retrieval.

The chunking strategy is designed for:
    - Resumes
    - Technical documents
    - Reports
    - Project documentation
    - Enterprise knowledge bases

Current strategy:
    - Character-based chunking
    - Larger context window
    - Controlled overlap
    - Preserves document order
"""


class ChunkingService:
    """
    Service responsible for splitting document text
    into embedding-friendly chunks.
    """

    DEFAULT_CHUNK_SIZE = 1500
    DEFAULT_CHUNK_OVERLAP = 250

    # ==========================================================
    # Chunk Text
    # ==========================================================

    def chunk_text(
        self,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        """
        Split document text into overlapping chunks.

        Args:
            text:
                Cleaned document text.

            chunk_size:
                Maximum approximate number of characters
                in each chunk.

            chunk_overlap:
                Number of characters shared between
                consecutive chunks.

        Returns:
            Ordered list of text chunks.
        """

        # ------------------------------------------------------
        # Validation
        # ------------------------------------------------------

        if not text or not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        # ------------------------------------------------------
        # Clean text
        # ------------------------------------------------------

        text = text.strip()

        chunks = []

        start = 0
        text_length = len(text)

        # ------------------------------------------------------
        # Sequential chunking
        # ------------------------------------------------------

        while start < text_length:

            end = min(
                start + chunk_size,
                text_length,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            # Finished
            if end >= text_length:
                break

            # Move forward while preserving overlap
            start = end - chunk_overlap

        return chunks


# ==========================================================
# Singleton
# ==========================================================

chunking_service = ChunkingService()


# ==========================================================
# Backwards-Compatible Function
# ==========================================================

def chunk_text(
    text: str,
    chunk_size: int = ChunkingService.DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = ChunkingService.DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Backwards-compatible helper.

    Existing document-processing code can continue using:

        chunk_text(text)

    without requiring changes elsewhere.
    """

    return chunking_service.chunk_text(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )