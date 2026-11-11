
from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

query = text("""
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content
    FROM document_chunks dc
    JOIN documents d
        ON dc.document_id = d.id
    WHERE d.filename ILIKE :filename
    ORDER BY dc.chunk_index
""")

try:
    with engine.connect() as conn:
        rows = conn.execute(
            query,
            {"filename": "%Code_of_Conduct_and_Ethics%"}
        ).fetchall()

        print(f"\nTotal chunks found: {len(rows)}")

        for row in rows:
            print(f"\n{'=' * 80}")
            print(
                f"CHUNK ID: {row[0]} | "
                f"DOCUMENT ID: {row[1]} | "
                f"INDEX: {row[2]}"
            )
            print("=" * 80)
            print(row[3])

except Exception as e:
    print(f"Database query failed: {e}")
