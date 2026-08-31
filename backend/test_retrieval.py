"""
Retrieval Service Test

Tests semantic search against the real indexed document.
"""

from database.database import SessionLocal
from services.retrieval_service import retrieval_service


def main():

    print("=" * 60)
    print("RAG RETRIEVAL TEST")
    print("=" * 60)

    db = SessionLocal()

    try:

        query = (
            "What is the proposed system for detecting "
            "potholes and monitoring road conditions?"
        )

        print(f"\nQuery:\n{query}")
        print("\nSearching...")
        print("-" * 60)

        results = retrieval_service.search(
            db=db,
            query=query,
            top_k=5,
        )

        if not results:

            print("No results found.")
            return

        print(
            f"\nRetrieved {len(results)} chunks:\n"
        )

        for i, result in enumerate(results, start=1):

            print("=" * 60)

            print(f"Result       : {i}")
            print(f"Chunk ID     : {result['chunk_id']}")
            print(
                f"Document ID  : "
                f"{result['document_id']}"
            )
            print(
                f"Chunk Index  : "
                f"{result['chunk_index']}"
            )
            print(
                f"Score        : "
                f"{result['score']:.4f}"
            )
            print(
                f"FAISS ID     : "
                f"{result['faiss_id']}"
            )

            print("\nContent:")
            print(result["content"][:500])

        print("\n" + "=" * 60)
        print("SUCCESS: Retrieval is working.")
        print("=" * 60)

    finally:

        db.close()


if __name__ == "__main__":
    main()