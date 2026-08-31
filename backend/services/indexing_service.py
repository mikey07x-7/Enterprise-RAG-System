"""
Document Indexing Service

Connects PostgreSQL document chunks with the
embedding service and FAISS vector store.
"""

from sqlalchemy.orm import Session

from models.chunk import Chunk
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store
from core.logger import logger


class IndexingService:
    """
    Converts document chunks into embeddings
    and stores them in the FAISS vector index.
    """

    def index_document(
        self,
        db: Session,
        document_id: int,
    ) -> int:
        """
        Generate embeddings for all chunks belonging
        to a document and add them to FAISS.

        Returns:
            Number of indexed chunks.
        """

        chunks = (
            db.query(Chunk)
            .filter(
                Chunk.document_id == document_id
            )
            .order_by(Chunk.chunk_index)
            .all()
        )

        if not chunks:
            raise ValueError(
                f"No chunks found for document "
                f"{document_id}."
            )

        logger.info(
            f"Indexing document {document_id}: "
            f"{len(chunks)} chunks"
        )

        # --------------------------------------------------
        # Extract chunk text
        # --------------------------------------------------

        texts = [
            chunk.content
            for chunk in chunks
        ]

        chunk_ids = [
            chunk.id
            for chunk in chunks
        ]

        # --------------------------------------------------
        # Generate embeddings
        # --------------------------------------------------

        logger.info(
            "Generating embeddings..."
        )

        embeddings = (
            embedding_service.embed_texts(
                texts
            )
        )

        # --------------------------------------------------
        # Store in FAISS
        # --------------------------------------------------

        logger.info(
            "Adding embeddings to FAISS..."
        )

        vector_store.add_embeddings(
            embeddings=embeddings,
            chunk_ids=chunk_ids,
        )

        logger.success(
            f"Document {document_id} indexed "
            f"successfully: {len(chunks)} chunks"
        )

        return len(chunks)


indexing_service = IndexingService()