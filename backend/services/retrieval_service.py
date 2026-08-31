"""
Retrieval Service

Handles semantic retrieval of relevant document chunks
using FAISS and PostgreSQL.

IMPORTANT:
Retrieval is USER-SCOPED.

A user can only retrieve chunks belonging to
documents owned by that authenticated user.
"""

from sqlalchemy.orm import Session

from core.logger import logger
from models.chunk import Chunk
from models.document import Document

from services.embedding_service import embedding_service
from services.vector_store_service import vector_store


class RetrievalService:
    """
    Retrieves relevant document chunks using semantic similarity.

    All retrieval operations are restricted to the
    authenticated user's documents.
    """

    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    # ======================================================
    # Semantic Search
    # ======================================================

    def search(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Retrieve the most relevant document chunks
        belonging ONLY to the specified user.

        Process:

        User Query
            ↓
        Query Embedding
            ↓
        FAISS Similarity Search
            ↓
        Chunk IDs
            ↓
        PostgreSQL
            ↓
        Verify Document Ownership
            ↓
        User's Chunks Only
        """

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if user_id is None:
            raise ValueError(
                "user_id is required for retrieval."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        logger.info(
            f"Retrieving chunks for user {user_id}: "
            f"{query}"
        )

        # --------------------------------------------------
        # 1. Generate query embedding
        # --------------------------------------------------

        query_embedding = (
            self.embedding_service.embed_text(query)
        )

        # --------------------------------------------------
        # 2. Search FAISS
        # --------------------------------------------------

        vector_results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
        )

        if not vector_results:

            logger.warning(
                f"No FAISS results found for user {user_id}."
            )

            return []

        logger.info(
            f"FAISS returned {len(vector_results)} candidates."
        )

        # --------------------------------------------------
        # 3. Retrieve chunks from PostgreSQL
        # --------------------------------------------------

        results = []

        for result in vector_results:

            chunk_id = result["chunk_id"]

            # --------------------------------------------------
            # IMPORTANT SECURITY CHECK
            #
            # Join Chunk -> Document and verify that
            # the document belongs to the authenticated user.
            # --------------------------------------------------

            chunk = (
                db.query(Chunk)
                .join(
                    Document,
                    Chunk.document_id == Document.id,
                )
                .filter(
                    Chunk.id == chunk_id,
                    Document.user_id == user_id,
                )
                .first()
            )

            # --------------------------------------------------
            # Chunk does not belong to this user
            # --------------------------------------------------

            if chunk is None:

                logger.warning(
                    f"Skipping chunk {chunk_id}: "
                    f"not owned by user {user_id}."
                )

                continue

            # --------------------------------------------------
            # Valid user-owned chunk
            # --------------------------------------------------

            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "score": result["score"],
                    "faiss_id": result["faiss_id"],
                }
            )

        logger.success(
            f"Retrieved {len(results)} user-owned chunks "
            f"for user {user_id}."
        )

        return results


# ==========================================================
# Singleton Instance
# ==========================================================

retrieval_service = RetrievalService()