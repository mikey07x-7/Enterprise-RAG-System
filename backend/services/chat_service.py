"""
RAG Chat Service

Combines:
- Query embedding
- Semantic retrieval
- Context construction
- Groq LLM generation
"""

from sqlalchemy.orm import Session

from core.logger import logger
from services.retrieval_service import retrieval_service
from services.llm_service import llm_service


SYSTEM_PROMPT = """
You are an Enterprise RAG assistant.

Your job is to answer questions using ONLY the
information provided in the retrieved document context.

Rules:

1. Use the provided context as the primary source of truth.
2. Do not invent facts.
3. Do not use outside knowledge when answering
   document-specific questions.
4. If the answer cannot be found in the context,
   clearly say that the information was not found
   in the provided documents.
5. Give concise but informative answers.
6. When possible, mention the relevant document
   and section information.
"""


class ChatService:
    """
    Complete Retrieval-Augmented Generation pipeline.
    """

    def ask(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
    ) -> dict:

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query = query.strip()

        logger.info(
            f"RAG query received: {query}"
        )

        # --------------------------------------------------
        # 1. Retrieve relevant chunks
        # --------------------------------------------------

        results = retrieval_service.search(
            db=db,
            query=query,
            top_k=top_k,
        )

        if not results:

            return {
                "answer": (
                    "I could not find relevant "
                    "information in the uploaded documents."
                ),
                "sources": [],
            }

        logger.info(
            f"Retrieved {len(results)} chunks."
        )

        # --------------------------------------------------
        # 2. Build context
        # --------------------------------------------------

        context_parts = []

        for index, result in enumerate(results, start=1):

            context_parts.append(
                f"""
--- SOURCE {index} ---
Document ID: {result["document_id"]}
Chunk ID: {result["chunk_id"]}
Similarity Score: {result["score"]:.4f}

{result["content"]}
"""
            )

        context = "\n".join(context_parts)

        # --------------------------------------------------
        # 3. Build RAG prompt
        # --------------------------------------------------

        prompt = f"""
Answer the user's question using the retrieved
document context below.

USER QUESTION:
{query}

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:

- Answer only from the retrieved context.
- Do not fabricate information.
- If the context does not contain the answer,
  say that the answer was not found in the
  provided documents.
- Explain the answer clearly.
"""

        # --------------------------------------------------
        # 4. Generate answer
        # --------------------------------------------------

        answer = llm_service.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=1000,
        )

        # --------------------------------------------------
        # 5. Prepare sources
        # --------------------------------------------------

        sources = []

        for result in results:

            sources.append(
                {
                    "document_id": result["document_id"],
                    "chunk_id": result["chunk_id"],
                    "score": result["score"],
                }
            )

        logger.success(
            "RAG answer generated successfully."
        )

        return {
            "answer": answer,
            "sources": sources,
        }


chat_service = ChatService()