"""
Embedding Service

Generates vector embeddings for document chunks
using a SentenceTransformer embedding model.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from core.config import settings
from core.logger import logger


class EmbeddingService:
    """
    Handles generation of embeddings for text.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL

        logger.info(
            f"Loading embedding model: {self.model_name}"
        )

        self.model = SentenceTransformer(self.model_name)

        logger.success(
            f"Embedding model loaded: {self.model_name}"
        )

    # ======================================================
    # Single Text
    # ======================================================

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text string.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    # ======================================================
    # Multiple Texts
    # ======================================================

    def embed_texts(
        self,
        texts: list[str],
        batch_size: int = 32,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple text strings.
        """

        if not texts:
            return []

        if any(
            not text or not text.strip()
            for text in texts
        ):
            raise ValueError(
                "Texts cannot contain empty values."
            )

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    # ======================================================
    # Embedding Dimension
    # ======================================================

    def get_embedding_dimension(self) -> int:
        """
        Return the dimensionality of the embedding vectors.
        """

        return self.model.get_sentence_embedding_dimension()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """
    Return a cached EmbeddingService instance.
    """

    return EmbeddingService()


embedding_service = get_embedding_service()