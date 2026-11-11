
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from services.retrieval_service import retrieval_service

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

query = (
    "An employee discovers suspected financial fraud involving "
    "a senior manager but fears retaliation. Explain reporting "
    "channels, anonymous reporting, investigation timelines, "
    "protection against retaliation, and disciplinary consequences."
)

db = SessionLocal()

try:
    results = retrieval_service.search(
        db=db,
        query=query,
        user_id=1,  # Replace with the ID of the user who uploaded the documents
        top_k=30
    )

    print(f"\nRetrieved chunks: {len(results)}")

    for i, result in enumerate(results, 1):
        if result["chunk_id"] in [215, 216, 217, 220, 221]:
            print("\n" + "=" * 70)
            print(f"RANK: {i}")
            print(f"CHUNK ID: {result['chunk_id']}")
            print(f"RRF SCORE: {result['score']:.6f}")
            print(f"SEMANTIC RANK: {result.get('semantic_rank')}")
            print(f"LEXICAL RANK: {result.get('lexical_rank')}")
            print(f"CONTENT: {result['content']}")
finally:
    db.close()
