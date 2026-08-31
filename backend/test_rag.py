from database.database import SessionLocal
from services.rag_service import rag_service


print("=" * 60)
print("COMPLETE RAG PIPELINE TEST")
print("=" * 60)

query = (
    "What is the proposed system for detecting potholes "
    "and monitoring road conditions?"
)

print("\nQuery:")
print(query)

print("\nRunning RAG pipeline...")
print("-" * 60)

db = SessionLocal()

try:

    result = rag_service.generate_answer(
        db=db,
        query=query,
        top_k=5,
    )

    print("\nANSWER")
    print("=" * 60)

    print(result["answer"])

    print("\nSOURCES")
    print("=" * 60)

    for source in result["sources"]:

        print(
            f"Document ID : {source['document_id']}"
        )

        print(
            f"Chunk ID     : {source['chunk_id']}"
        )

        print(
            f"Chunk Index  : {source['chunk_index']}"
        )

        print(
            f"Similarity   : {source['score']:.4f}"
        )

        print("-" * 40)

    print("\n" + "=" * 60)
    print("SUCCESS: COMPLETE RAG PIPELINE IS WORKING.")
    print("=" * 60)

finally:

    db.close()