import chromadb
from openai import OpenAI
from app.rag.extractor import extract_schema
import os 
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


#ChromaDB stored locally 
chroma_client = chromadb.PersistentClient(path="./chroma_db")

COLLECTION_NAME = "schema_chunks"

def embed_text(text:str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def index_schema():
    #DELETE AND RECREATE SO RERUN STAYS CLEAN

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
            metadatas=[{"table": chunk["table_name"]}]
        )
        print(f"  Indexed: {chunk['table_name']}")

    print(f"\nDone. {len(chunks)} tables indexed into ChromaDB.")
    return collection


if __name__ == "__main__":
    index_schema()

