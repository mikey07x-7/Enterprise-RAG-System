"""
FAISS Vector Store Service

Handles:
- Creating the FAISS index
- Adding document chunk embeddings
- Persisting the index
- Loading the index
- Similarity search
"""

import json
from pathlib import Path

import faiss
import numpy as np

from core.config import settings
from core.logger import logger


class VectorStoreService:
    """
    Manages the FAISS vector index used by the RAG system.
    """

    def __init__(self):
        self.dimension = 768

        self.storage_dir = (
            Path(__file__).resolve().parent.parent
            / "storage"
            / "vectorstore"
        )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            self.storage_dir / "documents.index"
        )

        self.mapping_path = (
            self.storage_dir / "chunk_mapping.json"
        )

        self.index = None
        self.chunk_mapping = {}

        self.load_or_create()

    # ======================================================
    # Index Management
    # ======================================================

    def create_index(self):
        """
        Create a new FAISS cosine-similarity index.

        Because embeddings are normalized, inner product
        is equivalent to cosine similarity.
        """

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.chunk_mapping = {}

        logger.info(
            f"Created FAISS index with dimension {self.dimension}"
        )

    def load_or_create(self):
        """
        Load an existing FAISS index if available.
        Otherwise create a new one.
        """

        if self.index_path.exists():

            self.index = faiss.read_index(
                str(self.index_path)
            )

            logger.success(
                f"Loaded FAISS index: "
                f"{self.index.ntotal} vectors"
            )

            if self.mapping_path.exists():

                with open(
                    self.mapping_path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    self.chunk_mapping = json.load(
                        file
                    )

        else:

            self.create_index()

    # ======================================================
    # Persistence
    # ======================================================

    def save(self):
        """
        Save FAISS index and chunk mapping to disk.
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been initialized."
            )

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        with open(
            self.mapping_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.chunk_mapping,
                file,
                indent=4,
            )

        logger.success(
            f"Vector store saved: "
            f"{self.index.ntotal} vectors"
        )

    # ======================================================
    # Add Embeddings
    # ======================================================

    def add_embeddings(
        self,
        embeddings: list[list[float]],
        chunk_ids: list[int],
    ):
        """
        Add embeddings to the FAISS index.

        Each embedding is associated with a
        PostgreSQL document chunk ID.
        """

        if len(embeddings) != len(chunk_ids):
            raise ValueError(
                "Number of embeddings must match "
                "number of chunk IDs."
            )

        if not embeddings:
            return

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension "
                f"{self.dimension}, "
                f"got {vectors.shape[1]}."
            )

        start_index = self.index.ntotal

        self.index.add(vectors)

        for offset, chunk_id in enumerate(chunk_ids):

            faiss_id = start_index + offset

            self.chunk_mapping[str(faiss_id)] = (
                chunk_id
            )

        self.save()

        logger.success(
            f"Added {len(embeddings)} embeddings "
            f"to FAISS."
        )

    # ======================================================
    # Search
    # ======================================================

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ):
        """
        Search for the most similar chunks.
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index is not initialized."
            )

        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal),
        )

        results = []

        for score, faiss_id in zip(
            scores[0],
            indices[0],
        ):

            if faiss_id == -1:
                continue

            chunk_id = self.chunk_mapping.get(
                str(int(faiss_id))
            )

            if chunk_id is None:
                continue

            results.append(
                {
                    "chunk_id": chunk_id,
                    "score": float(score),
                    "faiss_id": int(faiss_id),
                }
            )

        return results

    # ======================================================
    # Statistics
    # ======================================================

    def count(self) -> int:
        """
        Return the number of vectors in the index.
        """

        if self.index is None:
            return 0

        return self.index.ntotal


vector_store = VectorStoreService()