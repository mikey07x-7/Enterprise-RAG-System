"""
RAG Service

Combines:

1. Semantic retrieval using FAISS
2. PostgreSQL chunk retrieval
3. User-level document isolation
4. Context construction
5. Groq LLM generation

Pipeline:

User Query
    ↓
Query Embedding
    ↓
FAISS Retrieval
    ↓
User Ownership Filtering
    ↓
Relevant Chunks
    ↓
Context Construction
    ↓
Groq LLM
    ↓
Grounded Answer
"""

from sqlalchemy.orm import Session

from core.logger import logger
from services.retrieval_service import retrieval_service
from llm.groq_client import groq_client


class RAGService:
    """
    Main Retrieval-Augmented Generation service.

    Responsible for:

        - Retrieving relevant document chunks
        - Enforcing user-level document isolation
        - Building the LLM context
        - Generating a grounded answer
        - Returning source information
    """

    # ==========================================================
    # System Prompt
    # ==========================================================

    SYSTEM_PROMPT = """
You are an Enterprise RAG assistant.

Your task is to answer questions using ONLY the
information provided in the retrieved document context.

Rules:

1. Use the retrieved context as the primary source of truth.
2. Do not invent facts that are not present in the context.
3. Do not use outside knowledge for document-specific questions.
4. If the context does not contain enough information,
   clearly say that the information is not available
   in the provided documents.
5. Give a concise but useful answer.
6. When appropriate, organize the answer using bullet points.
7. When possible, mention the relevant document or section.
8. Do not mention internal implementation details such as
   FAISS, embeddings, vector databases, or retrieval
   unless the user explicitly asks about the RAG system.
"""

    # ==========================================================
    # Initialization
    # ==========================================================

    def __init__(self):

        self.retrieval_service = retrieval_service
        self.llm = groq_client

        logger.info(
            "RAG service initialized successfully."
        )

    # ==========================================================
    # Build Context
    # ==========================================================

    def build_context(
        self,
        retrieved_chunks: list[dict],
    ) -> str:
        """
        Convert retrieved chunks into an LLM-ready context.
        """

        if not retrieved_chunks:
            return ""

        context_parts = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):

            context_parts.append(
                f"""
[Context {index}]
Document ID: {chunk["document_id"]}
Chunk ID: {chunk["chunk_id"]}
Chunk Index: {chunk["chunk_index"]}
Similarity Score: {chunk["score"]:.4f}

Content:
{chunk["content"]}
"""
            )

        return "\n".join(
            context_parts
        ).strip()

    # ==========================================================
    # Generate Answer
    # ==========================================================

    def generate_answer(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> dict:
        """
        Execute the complete user-scoped RAG pipeline.

        Args:

            db:
                SQLAlchemy database session.

            query:
                User question.

            user_id:
                Authenticated user's ID.

            top_k:
                Number of chunks to retrieve.

        Returns:

            {
                "query": str,
                "answer": str,
                "sources": list
            }
        """

        # ======================================================
        # 1. Validate query
        # ======================================================

        if not query or not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        if user_id is None:

            raise ValueError(
                "user_id is required."
            )

        query = query.strip()

        logger.info(
            f"Starting RAG generation for "
            f"user {user_id}: {query}"
        )

        # ======================================================
        # 2. Retrieve USER-OWNED chunks
        # ======================================================

        logger.info(
            f"Retrieving top {top_k} chunks "
            f"for user {user_id}."
        )

        retrieved_chunks = (
            self.retrieval_service.search(
                db=db,
                query=query,
                user_id=user_id,
                top_k=top_k,
            )
        )

        logger.info(
            f"Retrieved {len(retrieved_chunks)} "
            f"user-owned chunks."
        )

        # ======================================================
        # 3. Handle no relevant context
        # ======================================================

        if not retrieved_chunks:

            logger.warning(
                f"No relevant document context "
                f"found for user {user_id}."
            )

            return {
                "query": query,
                "answer": (
                    "I could not find relevant information "
                    "in your available documents."
                ),
                "sources": [],
            }

        # ======================================================
        # 4. Build context
        # ======================================================

        context = self.build_context(
            retrieved_chunks
        )

        if not context:

            logger.warning(
                "Retrieved chunks produced empty context."
            )

            return {
                "query": query,
                "answer": (
                    "I could not find enough information "
                    "in your available documents."
                ),
                "sources": [],
            }

        logger.info(
            "User-scoped RAG context constructed successfully."
        )

        # ======================================================
        # 5. Build LLM prompt
        # ======================================================

        user_prompt = f"""
Answer the following question using ONLY the
retrieved document context.

USER QUESTION:
{query}

RETRIEVED DOCUMENT CONTEXT:
{context}

INSTRUCTIONS:

- Answer only from the retrieved context.
- Do not fabricate or assume information.
- Do not use external knowledge.
- If the answer cannot be found in the context,
  clearly state that the information was not found
  in the provided documents.
- Give a clear and useful answer.
- Use bullet points when they improve readability.
"""

        logger.info(
            "Sending user-scoped RAG prompt to LLM."
        )

        # ======================================================
        # 6. Generate answer
        # ======================================================

        answer = self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=2048,
        )

        if not answer or not answer.strip():

            logger.warning(
                "LLM returned an empty answer."
            )

            answer = (
                "I was unable to generate an answer "
                "from the provided documents."
            )

        answer = answer.strip()

        # ======================================================
        # 7. Prepare source information
        # ======================================================

        sources = []

        for chunk in retrieved_chunks:

            sources.append(
                {
                    "document_id": chunk["document_id"],
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk["chunk_index"],
                    "score": float(chunk["score"]),
                }
            )

        # ======================================================
        # 8. Return result
        # ======================================================

        logger.success(
            f"RAG answer generated successfully "
            f"for user {user_id}."
        )

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
        }


# ==========================================================
# Singleton
# ==========================================================

rag_service = RAGService()