"""
Document Service

Handles document creation, processing, chunk storage,
and FAISS indexing.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from core.logger import logger
from models.document import Document
from models.chunk import Chunk
from services.chunking_service import chunking_service
from services.indexing_service import indexing_service
from services.upload_service import (
    validate_file_type,
    extract_document_pages,
    extract_text,  # Backward-compatible import used by existing tests/scripts.
    DocumentProcessingError,
)


def process_and_store_document(
    db: Session,
    file_path: str | Path,
    user_id: int,
    filename: str | None = None,
) -> Document:
    """
    Complete document processing pipeline.

    Pipeline:

        File
          ↓
        Text Extraction
          ↓
        Chunking
          ↓
        PostgreSQL
          ↓
        Embeddings
          ↓
        FAISS
          ↓
        ready
    """

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"File does not exist: {path}"
        )

    if not validate_file_type(path):
        raise DocumentProcessingError(
            f"Unsupported file type: {path.suffix}"
        )

    document = None

    try:
        # ==================================================
        # 1. Extract text
        # ==================================================

        logger.info(
            f"Extracting text from: {path.name}"
        )

        pages = extract_document_pages(path)
        text = "\n\n".join(page["text"] for page in pages)

        if not text.strip():
            raise DocumentProcessingError(
                "No readable text was extracted."
            )

        # ==================================================
        # 2. Create document record
        # ==================================================

        document = Document(
            user_id=user_id,
            filename=filename or path.name,
            file_type=path.suffix.lower().lstrip("."),
            file_path=str(path),
            title=Path(filename or path.name).stem,
            status="processing",
        )

        db.add(document)
        db.flush()

        logger.info(
            f"Created document record: {document.id}"
        )

        # ==================================================
        # 3. Chunk document
        # ==================================================

        logger.info(
            f"Chunking document {document.id}"
        )

        chunks = chunking_service.chunk_pages(
            pages,
            chunk_size=1200,
            chunk_overlap=180,
        )

        if not chunks:
            raise DocumentProcessingError(
                "No chunks were generated."
            )

        # ==================================================
        # 4. Store chunks
        # ==================================================

        for index, chunk_data in enumerate(chunks):
            chunk = Chunk(
                document_id=document.id,
                chunk_index=index,
                page_number=chunk_data.get("page_number"),
                section_title=chunk_data.get("section_title"),
                content=chunk_data["content"],
            )

            db.add(chunk)

        db.flush()

        logger.success(
            f"Created {len(chunks)} chunks "
            f"for document {document.id}"
        )

        # ==================================================
        # 5. Generate embeddings + FAISS
        # ==================================================

        logger.info(
            f"Indexing document {document.id}"
        )

        indexed_count = indexing_service.index_document(
            db=db,
            document_id=document.id,
        )

        if indexed_count != len(chunks):
            raise DocumentProcessingError(
                "FAISS indexing count does not match "
                "the number of document chunks."
            )

        # ==================================================
        # 6. Mark as ready
        # ==================================================

        document.status = "ready"

        db.commit()
        db.refresh(document)

        logger.success(
            f"Document {document.id} processed successfully "
            f"with {indexed_count} indexed chunks."
        )

        return document

    except Exception as exc:

        db.rollback()
        # Remove any FAISS rows that may have been written before the DB rollback.
        try:
            indexing_service.rebuild_index(db)
        except Exception:
            logger.exception("FAISS reconciliation after document rollback failed.")

        logger.exception(
            f"Document processing failed: {exc}"
        )

        raise