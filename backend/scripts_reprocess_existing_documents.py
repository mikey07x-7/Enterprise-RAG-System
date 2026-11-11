"""Safely regenerate page/section-aware chunks for existing ready documents.

Run from the backend directory after backing up PostgreSQL and storage/vectorstore.
Preserves document rows/IDs/user ownership and source files. Replaces only each
selected document's Chunk rows, then rebuilds FAISS once after the DB commit.
"""
from pathlib import Path
from collections import defaultdict

from database.database import SessionLocal
from models.document import Document
from models.chunk import Chunk
from services.upload_service import extract_document_pages
from services.chunking_service import chunking_service
from services.indexing_service import indexing_service

BACKEND_DIR = Path(__file__).resolve().parent


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (BACKEND_DIR / path).resolve()


def main() -> None:
    db = SessionLocal()
    try:
        documents = (db.query(Document)
                     .filter(Document.status == "ready")
                     .order_by(Document.id)
                     .all())
        if not documents:
            print("No ready documents found. Nothing to reprocess.")
            return

        # Report duplicate physical files, but preserve every document row and owner.
        duplicate_groups = defaultdict(list)
        for doc in documents:
            duplicate_groups[(doc.user_id, str(resolve_path(doc.file_path)).casefold())].append(doc.id)
        for (_, path_key), ids in duplicate_groups.items():
            if len(ids) > 1:
                print(f"DUPLICATE SOURCE PATH: document IDs {ids} -> {path_key}")

        staged = []
        for doc in documents:
            source = resolve_path(doc.file_path)
            if not source.is_file():
                raise FileNotFoundError(f"Document {doc.id} source file is missing: {source}")
            pages = extract_document_pages(source)
            chunks = chunking_service.chunk_pages(pages, chunk_size=1200, chunk_overlap=180)
            if not chunks:
                raise RuntimeError(f"No chunks generated for document {doc.id} ({doc.filename})")
            staged.append((doc, chunks))
            page_count = sum(1 for p in pages if p.get("page_number") is not None)
            section_count = sum(1 for c in chunks if c.get("section_title"))
            print(f"PREPARED document={doc.id} file={doc.filename} pages={page_count} chunks={len(chunks)} section_tagged_chunks={section_count}")

        # Replace chunk rows in one DB transaction. Document IDs and user IDs remain unchanged.
        total_chunks = 0
        for doc, chunks in staged:
            db.query(Chunk).filter(Chunk.document_id == doc.id).delete(synchronize_session=False)
            for index, item in enumerate(chunks):
                db.add(Chunk(
                    document_id=doc.id,
                    chunk_index=index,
                    page_number=item.get("page_number"),
                    section_title=item.get("section_title"),
                    content=item["content"],
                ))
            total_chunks += len(chunks)

        db.commit()
        print(f"DATABASE UPDATED: {len(staged)} document records, {total_chunks} chunks")

        # Rebuild FAISS from committed DB rows. If this fails, rerun this script;
        # the source files and document records remain intact.
        indexed = indexing_service.rebuild_index(db)
        print(f"FAISS REBUILT: {indexed} vectors")

        page_tagged = db.query(Chunk).filter(Chunk.page_number.isnot(None)).count()
        section_tagged = db.query(Chunk).filter(Chunk.section_title.isnot(None)).count()
        db_total = db.query(Chunk).count()
        print(f"VERIFICATION: chunks={db_total}, page_tagged={page_tagged}, section_tagged={section_tagged}")
        if indexed != db_total:
            raise RuntimeError(f"FAISS vector count ({indexed}) does not match DB chunk count ({db_total}).")
        if page_tagged == 0:
            print("WARNING: No page metadata was produced. Check whether the source documents are PDFs.")
        if section_tagged == 0:
            print("WARNING: No section headings were detected. Inspect extracted PDF text and heading format.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
