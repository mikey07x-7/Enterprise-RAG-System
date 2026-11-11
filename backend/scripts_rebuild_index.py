"""Rebuild the FAISS index from PostgreSQL chunks.

Run from backend directory:
    python scripts_rebuild_index.py
This rebuilds vectors only; existing legacy chunks will keep NULL page/section metadata.
For page-aware citations, re-upload/reprocess source documents after applying the migration.
"""
from database.database import SessionLocal
from services.indexing_service import indexing_service


def main():
    db = SessionLocal()
    try:
        count = indexing_service.rebuild_index(db)
        print(f"FAISS index rebuilt successfully: {count} chunks")
    finally:
        db.close()


if __name__ == "__main__":
    main()
