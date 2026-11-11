"""Document indexing with full-index rebuilds to prevent stale/duplicate FAISS rows."""
from sqlalchemy.orm import Session
from models.chunk import Chunk
from models.document import Document
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store
from core.logger import logger

class IndexingService:
    def rebuild_index(self, db: Session) -> int:
        """Re-embed all chunks belonging to ready/processing documents and replace FAISS."""
        rows = (db.query(Chunk)
                .join(Document, Chunk.document_id == Document.id)
                .filter(Document.status.in_(["ready", "processing"]))
                .order_by(Chunk.id)
                .all())
        if not rows:
            vector_store.replace_embeddings([], [])
            return 0
        embeddings = embedding_service.embed_texts([row.content for row in rows])
        vector_store.replace_embeddings(embeddings, [row.id for row in rows])
        logger.success("Rebuilt FAISS index with %d chunks.", len(rows))
        return len(rows)

    def index_document(self, db: Session, document_id: int) -> int:
        chunks = (db.query(Chunk).filter(Chunk.document_id == document_id)
                  .order_by(Chunk.chunk_index).all())
        if not chunks:
            raise ValueError(f"No chunks found for document {document_id}.")
        count = self.rebuild_index(db)
        if count < len(chunks):
            raise RuntimeError("FAISS rebuild did not include all document chunks.")
        return len(chunks)

indexing_service = IndexingService()
