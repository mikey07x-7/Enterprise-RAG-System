from services.embedding_service import embedding_service


def main():
    text = """
    The proposed system uses deep learning and computer vision
    for real-time pothole detection and road condition monitoring.
    """

    print("=" * 60)
    print("EMBEDDING SERVICE TEST")
    print("=" * 60)

    embedding = embedding_service.embed_text(text)

    print(f"Embedding dimension : {len(embedding)}")
    print(f"First 5 values      : {embedding[:5]}")

    print("=" * 60)
    print("SUCCESS: Embedding generated.")
    print("=" * 60)


if __name__ == "__main__":
    main()