"""User-scoped hybrid retrieval: FAISS semantic ranking + lexical BM25 + RRF."""
import math
import re
from collections import Counter
from sqlalchemy.orm import Session
from core.logger import logger
from models.chunk import Chunk
from models.document import Document
from services.embedding_service import embedding_service
from services.vector_store_service import vector_store

_TOKEN = re.compile(r"[a-z0-9]+", re.I)
def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "")]

def _bm25(query: str, documents: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Small dependency-free BM25 implementation for per-user candidate chunks."""
    tokenized = [_tokens(doc) for doc in documents]
    if not tokenized:
        return []
    qtokens = set(_tokens(query))
    lengths = [len(doc) for doc in tokenized]
    avg_len = sum(lengths) / max(len(lengths), 1)
    df = Counter(token for doc in tokenized for token in set(doc))
    scores = []
    n = len(tokenized)
    for tokens, length in zip(tokenized, lengths):
        tf = Counter(tokens)
        score = 0.0
        for term in qtokens:
            freq = tf.get(term, 0)
            if not freq:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            denom = freq + k1 * (1 - b + b * length / max(avg_len, 1))
            score += idf * (freq * (k1 + 1)) / denom
        scores.append(score)
    return scores

class RetrievalService:
    RRF_K = 60
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def search(self, db: Session, query: str, user_id: int, top_k: int = 12) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if user_id is None:
            raise ValueError("user_id is required for retrieval.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")
        query = query.strip()
        owned = (db.query(Chunk, Document).join(Document, Chunk.document_id == Document.id)
                 .filter(Document.user_id == user_id, Document.status == "ready")
                 .order_by(Chunk.id).all())
        if not owned:
            return []
        chunks = [row[0] for row in owned]
        by_id = {chunk.id: (chunk, doc) for chunk, doc in owned}

        # Semantic rank is calculated globally, then filtered by ownership.
        query_embedding = self.embedding_service.embed_text(query)
        vector_results = self.vector_store.search(query_embedding, top_k=self.vector_store.count()) if self.vector_store.count() else []
        semantic_rank = {}
        semantic_score = {}
        rank = 0
        for item in vector_results:
            cid = int(item["chunk_id"])
            if cid in by_id and cid not in semantic_rank:
                rank += 1
                semantic_rank[cid] = rank
                semantic_score[cid] = float(item["score"])

        lexical_scores = _bm25(query, [chunk.content for chunk in chunks])
        lexical_order = sorted(range(len(chunks)), key=lambda i: lexical_scores[i], reverse=True)
        lexical_rank = {chunks[i].id: rank + 1 for rank, i in enumerate(lexical_order) if lexical_scores[i] > 0}

        fused = []
        for chunk in chunks:
            cid = chunk.id
            sr = semantic_rank.get(cid)
            lr = lexical_rank.get(cid)
            if sr is None and lr is None:
                continue
            rrf = (1 / (self.RRF_K + sr) if sr else 0) + (1 / (self.RRF_K + lr) if lr else 0)
            doc = by_id[cid][1]
            fused.append((rrf, chunk, doc))
        fused.sort(key=lambda item: item[0], reverse=True)

        results = []
        seen_content = set()
        for rrf, chunk, doc in fused:
            normalized = " ".join(chunk.content.lower().split())
            if normalized in seen_content:
                continue
            seen_content.add(normalized)
            results.append({
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "filename": doc.filename,
                "document_title": doc.title or doc.filename,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "content": chunk.content,
                "score": float(rrf),
                "semantic_score": semantic_score.get(chunk.id),
                "semantic_rank": semantic_rank.get(chunk.id),
                "lexical_rank": lexical_rank.get(chunk.id),
            })
            if len(results) >= top_k:
                break
        logger.info("Hybrid retrieval returned %d chunks for user %s.", len(results), user_id)
        return results

retrieval_service = RetrievalService()
