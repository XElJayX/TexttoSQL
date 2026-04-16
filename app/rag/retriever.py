import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="./chroma_store")
COLLECTION_NAME = "schema_chunks"

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    return model.encode(text).tolist()

def retrieve_relevant_tables(question: str, top_k: int = 3) -> str:
    collection = chroma_client.get_collection(COLLECTION_NAME)
    query_embedding = embed_text(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_chunks = results["documents"][0]
    retrieved_tables = results["metadatas"][0]

    print(f"\nQuestion: {question}")
    print(f"Retrieved tables: {[t['table_name'] for t in retrieved_tables]}")

    return "\n\n".join(retrieved_chunks)

if __name__ == "__main__":
    questions = [
        "which companies have cancelled their subscriptions recently?",
        "which companies have cancelled?",
        "what is our monthly recurring revenue by plan?",
        "which users haven't logged in for more than 30 days?",
        "which features are used most by enterprise customers?",
    ]
    for q in questions:
        context = retrieve_relevant_tables(q)
        print("-" * 40)