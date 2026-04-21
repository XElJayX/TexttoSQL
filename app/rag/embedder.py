import chromadb
from fastembed import TextEmbedding
from app.rag.extractor import extract_schema

chroma_client = chromadb.PersistentClient(path="./chroma_store")
COLLECTION_NAME = "schema_chunks"

# This downloads once (~90MB) and caches locally after that
model = TextEmbedding("BAAI/bge-small-en-v1.5")

def embed_text(text: str) -> list[float]:
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()

def index_schema():
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(COLLECTION_NAME)
    chunks = extract_schema()

    print(f"Embedding {len(chunks)} table chunks...")

    for chunk in chunks:
        embedding = embed_text(chunk["chunk"])
        collection.add(
            ids=[chunk["table_name"]],
            embeddings=[embedding],
            documents=[chunk["chunk"]],
            metadatas=[{"table_name": chunk["table_name"]}]
        )
        print(f"  Indexed: {chunk['table_name']}")

    print(f"\nDone. {len(chunks)} tables indexed into ChromaDB.")

if __name__ == "__main__":
    index_schema()