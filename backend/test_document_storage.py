from database.database import SessionLocal
from services.document_service import process_and_store_document


TEST_FILE = "storage/uploads/test.pdf"

# Temporary test user.
# We will replace this with authentication later.
TEST_USER_ID = 1


def main():

    print("=" * 60)
    print("DOCUMENT DATABASE STORAGE TEST")
    print("=" * 60)

    db = SessionLocal()

    try:

        document = process_and_store_document(
            db=db,
            file_path=TEST_FILE,
            user_id=TEST_USER_ID,
            filename="test.pdf",
        )

        print("\nSUCCESS!")
        print(f"Document ID : {document.id}")
        print(f"Filename    : {document.filename}")
        print(f"File type   : {document.file_type}")
        print(f"Status      : {document.status}")
        print(f"Chunks      : {len(document.chunks)}")

    except Exception as exc:

        print("\nERROR:")
        print(exc)

    finally:

        db.close()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()