import chromadb
from fastembed import TextEmbedding

chroma_client = chromadb.PersistentClient(path="./chroma_store")
COLLECTION_NAME = "schema_chunks"

model = TextEmbedding("BAAI/bge-small-en-v1.5")

def embed_text(text: str) -> list[float]:
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()

def retrieve_relevant_tables(question: str, top_k: int = 4) -> str:
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

def retrieve_with_metadata(question: str, top_k: int = 4) -> dict:
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

    return {
        "tables": [t["table_name"] for t in retrieved_tables],
        "chunks": "\n\n".join(retrieved_chunks)
    }

if __name__ == "__main__":
    questions = [
    "which companies have cancelled their subscriptions recently?",
    "which users have never logged in?",
    "what is our monthly recurring revenue by plan?",
    "which features are used most by enterprise customers?",
    ]
    for q in questions:
        context = retrieve_relevant_tables(q)
        print("-" * 40)