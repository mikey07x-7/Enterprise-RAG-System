
"""
RAG Service

Combines:
1. User-scoped hybrid retrieval (FAISS + BM25)
2. Multi-query retrieval for complex questions
3. Reciprocal Rank Fusion (RRF)
4. Aspect-aware retrieval reservations
5. Context construction with document metadata
6. Grounded answer generation using Groq
"""

import csv
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

from sqlalchemy.orm import Session

from core.logger import logger
from services.retrieval_service import retrieval_service
from llm.groq_client import groq_client


class RAGService:
    """Main user-scoped Retrieval-Augmented Generation service."""

    RRF_K = 60

    SYSTEM_PROMPT = """
You are an Enterprise RAG assistant.

Answer questions using ONLY the retrieved document context.

Rules:
1. Use retrieved document context as the source of truth.
2. Never invent facts or use outside knowledge for
   document-specific questions.
3. Address every distinct part of the user's question.
4. For multi-part questions, organize answers into
   clearly labelled bullet points where appropriate.
5. Mention relevant document sections when available.
6. If a particular part is not supported by the context,
   explicitly say that the information was not found.
7. Do not claim information is unavailable if it is
   present anywhere in the supplied context.
8. Do not expose internal implementation details unless
   the user explicitly asks about the RAG system.
"""

    def __init__(self):
        self.retrieval_service = retrieval_service
        self.llm = groq_client
        self.evaluation_csv = (
            Path(__file__).resolve().parents[1]
            / "evaluation"
            / "results"
            / "rag_metrics.csv"
        )

        logger.info("RAG service initialized successfully.")

    def _record_evaluation(
        self,
        *,
        request_id: str,
        user_id: int,
        top_k: int,
        retrieval_seconds: float,
        generation_seconds: float,
        total_seconds: float,
        retrieved_chunks: int,
        source_documents: int,
        status: str,
    ) -> None:
        """Append one privacy-conscious timing record to the evaluation CSV."""
        columns = [
            "timestamp_utc", "request_id", "user_id", "top_k",
            "retrieval_seconds", "generation_seconds", "total_seconds",
            "retrieved_chunks", "source_documents", "status",
        ]
        try:
            self.evaluation_csv.parent.mkdir(parents=True, exist_ok=True)
            write_header = not self.evaluation_csv.exists() or self.evaluation_csv.stat().st_size == 0
            with self.evaluation_csv.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                if write_header:
                    writer.writeheader()
                writer.writerow({
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "request_id": request_id,
                    "user_id": user_id,
                    "top_k": top_k,
                    "retrieval_seconds": round(retrieval_seconds, 6),
                    "generation_seconds": round(generation_seconds, 6),
                    "total_seconds": round(total_seconds, 6),
                    "retrieved_chunks": retrieved_chunks,
                    "source_documents": source_documents,
                    "status": status,
                })
        except OSError:
            logger.exception("Could not write RAG evaluation metrics CSV.")

    # ------------------------------------------------------
    # 1. Focused query specifications
    # ------------------------------------------------------

    def get_priority_query_specs(self, query: str) -> list[tuple]:
        """
        Return important focused queries that must receive
        retrieval priority.

        Each tuple contains:
            (aspect_name, focused_search_query)
        """

        q = query.lower()
        specs = []

        travel_terms = (
            "travel",
            "trip",
            "business meeting",
            "business trip",
            "domestic",
            "international",
            "journey",
        )

        is_travel_question = any(
            term in q for term in travel_terms
        )

        # Travel booking requirements.
        if is_travel_question and any(
            term in q for term in (
                "short notice",
                "book",
                "booking",
                "advance",
                "travel",
                "trip",
                "meeting",
                "domestic",
                "international",
            )
        ):
            specs.append((
                "travel_booking",
                (
                    "TravelDesk portal business travel booking "
                    "domestic travel minimum 7 days in advance "
                    "international travel minimum 21 days in advance"
                ),
            ))

        # Travel approval requirements.
        if is_travel_question and any(
            term in q for term in (
                "approval",
                "approve",
                "approver",
                "short notice",
                "business",
                "trip",
                "travel",
                "cost",
                "meeting",
            )
        ):
            specs.append((
                "travel_approval",
                (
                    "business trip travel approval before booking "
                    "estimated total trip cost reporting manager "
                    "department head chief financial officer "
                    "INR 50000 INR 200000"
                ),
            ))

        # Expense submission and reimbursement.
        if is_travel_question and any(
            term in q for term in (
                "expense",
                "reimbursement",
                "claim",
                "personal car",
                "personal vehicle",
                "two-wheeler",
                "kilometre",
                "km",
            )
        ):
            specs.append((
                "travel_expense",
                (
                    "travel expense reimbursement claim Form TE-12 "
                    "30 days after trip end personal vehicle "
                    "car INR 12 per km two wheeler INR 5 per km"
                ),
            ))

        return specs

    # ------------------------------------------------------
    # 2. Generate focused search queries
    # ------------------------------------------------------

    def generate_search_queries(self, query: str) -> list[str]:
        """
        Generate deterministic focused queries.

        The original query is always retained.
        """

        queries = [query.strip()]

        # Split list-like and multi-part questions.
        fragments = re.split(
            r",|;|\band\b|\balso\b|\bas well as\b",
            query,
            flags=re.IGNORECASE,
        )

        for fragment in fragments:
            fragment = fragment.strip(" .?!:-\n\t")

            if len(fragment.split()) >= 3:
                queries.append(fragment)

        q = query.lower()

        # Existing Code of Conduct focused queries.
        if any(term in q for term in (
            "investigation",
            "investigate",
            "fraud",
            "ethics report",
            "whistleblower",
        )):
            queries.append(
                "investigation report acknowledgement "
                "begin investigation conclude completion "
                "working days timeline"
            )

        if any(term in q for term in (
            "retaliation",
            "retaliated",
            "fear",
            "protection",
            "whistleblower",
        )):
            queries.append(
                "retaliation protection good faith reporter "
                "employee reporting misconduct"
            )

        if any(term in q for term in (
            "anonymous",
            "anonymously",
            "confidential",
        )):
            queries.append(
                "anonymous reporting permitted confidential "
                "reporting ethics hotline"
            )

        if any(term in q for term in (
            "reporting channel",
            "reporting channels",
            "report misconduct",
            "report fraud",
            "whistleblower",
        )):
            queries.append(
                "reporting channels ethics hotline email "
                "compliance report"
            )

        if any(term in q for term in (
            "disciplinary",
            "misconduct",
            "fraud",
            "punishment",
            "termination",
        )):
            queries.append(
                "disciplinary action serious misconduct "
                "fraud suspension termination"
            )

        # Add focused travel queries.
        priority_specs = self.get_priority_query_specs(query)

        for _, focused_query in priority_specs:
            queries.append(focused_query)

        # Remove empty and duplicate queries.
        unique_queries = []
        seen = set()

        for item in queries:
            normalized = " ".join(item.lower().split())

            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_queries.append(item)

        logger.info(
            f"Generated {len(unique_queries)} search queries."
        )

        for index, item in enumerate(unique_queries, start=1):
            logger.debug(
                f"Search query {index}: {item}"
            )

        return unique_queries

    # ------------------------------------------------------
    # 3. Multi-query retrieval and RRF merging
    # ------------------------------------------------------

    def multi_query_search(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Execute user-scoped retrieval for multiple queries.

        Results are merged using RRF. Important focused
        aspects are reserved before filling remaining slots.
        """

        search_queries = self.generate_search_queries(query)

        priority_specs = self.get_priority_query_specs(query)

        # Map focused query strings to their aspect names.
        priority_query_map = {
            focused_query: aspect_name
            for aspect_name, focused_query in priority_specs
        }

        per_query_top_k = min(max(top_k, 8), 15)

        fused_scores = defaultdict(float)
        merged_chunks = {}
        original_ranks = {}

        # Store the best result for each priority aspect.
        priority_results = {}

        for search_query in search_queries:

            results = self.retrieval_service.search(
                db=db,
                query=search_query,
                user_id=user_id,
                top_k=per_query_top_k,
            )

            logger.info(
                f"Query retrieved {len(results)} chunks: "
                f"{search_query[:120]}"
            )

            # Capture the highest-ranked result from each
            # important focused search before RRF filtering.
            aspect_name = priority_query_map.get(search_query)

            if aspect_name and results:
                priority_results[aspect_name] = results[0]

                logger.info(
                    f"Priority result reserved for "
                    f"aspect '{aspect_name}': "
                    f"chunk_id={results[0]['chunk_id']}"
                )

            for rank, chunk in enumerate(results, start=1):

                chunk_id = chunk["chunk_id"]

                # Reciprocal Rank Fusion.
                fused_scores[chunk_id] += (
                    1.0 / (self.RRF_K + rank)
                )

                if chunk_id not in merged_chunks:
                    merged_chunks[chunk_id] = chunk

                if search_query == query:
                    original_ranks[chunk_id] = rank

        # Rank all merged chunks.
        ranked_chunks = sorted(
            merged_chunks.values(),
            key=lambda chunk: (
                fused_scores[chunk["chunk_id"]],
                -original_ranks.get(
                    chunk["chunk_id"],
                    10**6,
                ),
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # Aspect-aware selection
        # --------------------------------------------------

        selected_chunks = []
        selected_ids = set()

        def add_chunk(chunk):
            """Add a chunk once, preserving its metadata."""

            if not chunk:
                return

            chunk_id = chunk["chunk_id"]

            if chunk_id in selected_ids:
                return

            if len(selected_chunks) >= top_k:
                return

            selected_chunks.append(chunk)
            selected_ids.add(chunk_id)

        # Reserve one result for each priority aspect.
        # This prevents important travel requirements from
        # being removed by unrelated high-RRF results.
        for aspect_name, _ in priority_specs:

            reserved_chunk = priority_results.get(aspect_name)

            if reserved_chunk:
                logger.info(
                    f"Selecting priority aspect: {aspect_name}"
                )
                add_chunk(reserved_chunk)

        # Fill the remaining slots using normal RRF order.
        for chunk in ranked_chunks:

            if len(selected_chunks) >= top_k:
                break

            add_chunk(chunk)

        # Preserve retrieval score compatibility.
        for chunk in selected_chunks:
            chunk["multi_query_score"] = fused_scores.get(
                chunk["chunk_id"],
                0.0,
            )

        logger.info(
            f"Multi-query retrieval completed: "
            f"{len(merged_chunks)} unique chunks merged; "
            f"{len(selected_chunks)} selected; "
            f"{len(priority_results)} priority aspects reserved."
        )

        for index, chunk in enumerate(selected_chunks, start=1):
            logger.info(
                f"Selected chunk {index}: "
                f"file={chunk.get('filename')}, "
                f"section={chunk.get('section_title')}, "
                f"chunk_id={chunk.get('chunk_id')}, "
                f"rrf={chunk.get('multi_query_score', 0):.5f}"
            )

        return selected_chunks

    # ------------------------------------------------------
    # 4. Build context
    # ------------------------------------------------------

    def build_context(
        self,
        retrieved_chunks: list[dict],
    ) -> str:

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
Document: {chunk.get("filename", "Uploaded document")}
Document ID: {chunk["document_id"]}
Chunk ID: {chunk["chunk_id"]}
Chunk Index: {chunk["chunk_index"]}
Page: {chunk.get("page_number") or "Not available"}
Section: {chunk.get("section_title") or "Not identified"}
Retrieval Score: {chunk.get("multi_query_score", 0):.5f}

Content:
{chunk["content"]}
"""
            )

        return "\n".join(context_parts).strip()

    # ------------------------------------------------------
    # 5. Generate answer
    # ------------------------------------------------------

    def generate_answer(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = 10,
    ) -> dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if user_id is None:
            raise ValueError("user_id is required.")

        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError(
                "top_k must be a positive integer."
            )

        query = query.strip()
        request_id = str(uuid.uuid4())
        request_started = time.perf_counter()
        retrieval_started = time.perf_counter()

        logger.info(
            f"Starting multi-query RAG request {request_id} for user {user_id}."
        )

        # Retrieve chunks using authenticated user's ID.
        retrieved_chunks = self.multi_query_search(
            db=db,
            query=query,
            user_id=user_id,
            top_k=top_k,
        )
        retrieval_seconds = time.perf_counter() - retrieval_started

        if not retrieved_chunks:

            total_seconds = time.perf_counter() - request_started
            self._record_evaluation(
                request_id=request_id, user_id=user_id, top_k=top_k,
                retrieval_seconds=retrieval_seconds, generation_seconds=0.0,
                total_seconds=total_seconds, retrieved_chunks=0,
                source_documents=0, status="no_retrieved_context",
            )
            logger.warning(
                f"No relevant context found for user {user_id}."
            )

            return {
                "query": query,
                "answer": (
                    "I could not find relevant information "
                    "in your available documents."
                ),
                "sources": [],
            }

        context = self.build_context(retrieved_chunks)

        if not context:

            total_seconds = time.perf_counter() - request_started
            self._record_evaluation(
                request_id=request_id, user_id=user_id, top_k=top_k,
                retrieval_seconds=retrieval_seconds, generation_seconds=0.0,
                total_seconds=total_seconds, retrieved_chunks=len(retrieved_chunks),
                source_documents=len({c.get("document_id") for c in retrieved_chunks}),
                status="empty_context",
            )
            return {
                "query": query,
                "answer": (
                    "I could not find enough information "
                    "in your available documents."
                ),
                "sources": [],
            }

        # Build grounded LLM prompt.
        user_prompt = f"""
USER QUESTION:
{query}

RETRIEVED DOCUMENT CONTEXT:
{context}

INSTRUCTIONS:

- Answer every distinct aspect of the user's question.
- Use only the retrieved document context.
- Do not fabricate or assume information.
- Check all supplied context before deciding that
  information is unavailable.
- Do not confuse business travel with remote-work
  location approval or leave-notice requirements.
- If the question concerns short-notice travel, check
  the standard booking and approval requirements first.
- Do not invent exceptions or emergency approval processes.
- Keep different aspects of the answer clearly separated.
- Mention document section numbers when available.
- If one aspect is missing, identify only that aspect.
"""

        logger.info(
            f"Sending {len(retrieved_chunks)} merged chunks "
            f"to Groq for user {user_id}."
        )

        generation_started = time.perf_counter()
        answer = self.llm.generate(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=2048,
        )
        generation_seconds = time.perf_counter() - generation_started

        if not answer or not answer.strip():

            logger.warning("LLM returned an empty answer.")

            answer = (
                "I was unable to generate an answer "
                "from the provided documents."
            )

        answer = answer.strip()

        # --------------------------------------------------
        # 6. Prepare source information
        # --------------------------------------------------

        sources = []
        seen_source_chunks = set()

        for chunk in retrieved_chunks:

            chunk_id = chunk["chunk_id"]

            if chunk_id in seen_source_chunks:
                continue

            seen_source_chunks.add(chunk_id)

            sources.append({
                "document_id": chunk["document_id"],
                "chunk_id": chunk_id,
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk.get("page_number"),
                "section_title": chunk.get("section_title"),
                "score": float(chunk.get("score", 0)),
                "filename": chunk.get(
                    "filename",
                    "Document",
                ),
                "document_title": chunk.get(
                    "document_title",
                    chunk.get("filename", "Document"),
                ),
                "content": chunk["content"],
            })

        total_seconds = time.perf_counter() - request_started
        self._record_evaluation(
            request_id=request_id,
            user_id=user_id,
            top_k=top_k,
            retrieval_seconds=retrieval_seconds,
            generation_seconds=generation_seconds,
            total_seconds=total_seconds,
            retrieved_chunks=len(retrieved_chunks),
            source_documents=len({c.get("document_id") for c in retrieved_chunks}),
            status="success",
        )

        logger.success(
            f"Multi-query RAG answer generated successfully "
            f"for user {user_id}. "
            f"Retrieval={retrieval_seconds:.3f}s, "
            f"generation={generation_seconds:.3f}s, "
            f"total={total_seconds:.3f}s."
        )

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
        }


# ----------------------------------------------------------
# Singleton
# ----------------------------------------------------------

rag_service = RAGService()
