from services.embedding_service import embedding_service
from services.vector_store_service import vector_store


print("=" * 60)
print("FAISS VECTOR STORE TEST")
print("=" * 60)

texts = [
    "Enterprise RAG systems retrieve relevant documents.",
    "PostgreSQL stores structured application data.",
    "FAISS performs efficient vector similarity search.",
]

print("\nGenerating embeddings...")

embeddings = embedding_service.embed_texts(texts)

print(f"Generated embeddings : {len(embeddings)}")
print(f"Embedding dimension   : {len(embeddings[0])}")

chunk_ids = [1, 2, 3]

print("\nAdding embeddings to FAISS...")

vector_store.add_embeddings(
    embeddings=embeddings,
    chunk_ids=chunk_ids,
)

print(f"Vectors in index      : {vector_store.count()}")

print("\nSearching...")

query = (
    "How does the system search documents "
    "using vectors?"
)

query_embedding = embedding_service.embed_text(
    query
)

results = vector_store.search(
    query_embedding=query_embedding,
    top_k=3,
)

print("\nSearch Results:")
print("-" * 60)

for result in results:
    print(
        f"Chunk ID: {result['chunk_id']} | "
        f"Score: {result['score']:.4f} | "
        f"FAISS ID: {result['faiss_id']}"
    )

print("=" * 60)
print("SUCCESS: FAISS vector store is working.")
print("=" * 60)