from database.database import SessionLocal
from services.indexing_service import indexing_service
from services.vector_store_service import vector_store


DOCUMENT_ID = 1


print("=" * 60)
print("REAL DOCUMENT INDEXING TEST")
print("=" * 60)

db = SessionLocal()

try:

    print(
        f"\nIndexing document ID: {DOCUMENT_ID}"
    )

    count = indexing_service.index_document(
        db=db,
        document_id=DOCUMENT_ID,
    )

    print(
        f"\nChunks indexed : {count}"
    )

    print(
        f"FAISS vectors  : {vector_store.count()}"
    )

    print("=" * 60)
    print("SUCCESS: Real document indexed into FAISS.")
    print("=" * 60)

finally:

    db.close()