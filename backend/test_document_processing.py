from pathlib import Path

from services.document_service import extract_text
from services.chunking_service import chunk_text


TEST_FILE = Path("storage/uploads/test.pdf")


def main():

    print("=" * 60)
    print("DOCUMENT PROCESSING TEST")
    print("=" * 60)

    print(f"\nFile: {TEST_FILE}")

    if not TEST_FILE.exists():
        print("\nERROR: Test file does not exist.")
        print(f"Place a PDF at: {TEST_FILE}")
        return

    # Extract
    text = extract_text(TEST_FILE)

    print("\nExtraction successful!")
    print(f"Characters extracted: {len(text)}")

    # Preview
    print("\n--- TEXT PREVIEW ---")
    print(text[:1000])

    # Chunk
    chunks = chunk_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    print("\n--- CHUNKING ---")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {index}:")
        print(chunk[:500])

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()