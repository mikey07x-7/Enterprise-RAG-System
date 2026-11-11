
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from services.retrieval_service import retrieval_service

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

queries = [
    "How many working days does Compliance have to acknowledge a whistleblower report?",
    "When must an investigation into suspected fraud begin and conclude?",
    "What is the timeline for acknowledging, starting and completing an ethics investigation?",
    "investigation within 7 working days conclude within 45 days",
]

db = SessionLocal()

try:
    for query in queries:
        print("\n\n" + "#" * 90)
        print("QUERY:", query)
        print("#" * 90)

        results = retrieval_service.search(
            db=db,
            query=query,
            user_id=1,  # Use the correct document owner's ID
            top_k=5
        )

        for rank, result in enumerate(results, 1):
            print(
                f"\nRank {rank} | "
                f"Chunk {result['chunk_id']} | "
                f"Score {result['score']:.6f}"
            )
            print(result["content"])

finally:
    db.close()
