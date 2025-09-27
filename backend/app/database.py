import chromadb
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# Initialize embedding model
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# ChromaDB Collection Names updated to match your datasets
COLLECTION_ORDER_HISTORY = "Order_History"
COLLECTION_MYNTRA_CATALOG = "myntra202305041052"
COLLECTION_CELEB_STYLES = "Celeb_FBI_Dataset"

def get_chroma_client():
    """Returns the HTTP client to connect to the dedicated ChromaDB server."""
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        client.list_collections() 
        return client
    except Exception as e:
        print(f"Error connecting to ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT}. Ensure the server is running.")
        print(f"Error details: {e}")
        return None

def setup_collections(client):
    """Creates the necessary collections if they don't exist."""
    if not client:
        return {}
    collections = {}
    collections[COLLECTION_ORDER_HISTORY] = client.get_or_create_collection(name=COLLECTION_ORDER_HISTORY)
    collections[COLLECTION_MYNTRA_CATALOG] = client.get_or_create_collection(name=COLLECTION_MYNTRA_CATALOG)
    collections[COLLECTION_CELEB_STYLES] = client.get_or_create_collection(name=COLLECTION_CELEB_STYLES)
    print("ChromaDB collections verified/created successfully.")
    return collections

def create_embedding(text):
    """Create embedding for given text."""
    try:
        return EMBEDDING_MODEL.encode(text).tolist()
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None

def process_and_add_item(collection, text, metadata, item_id):
    """Process and add item to collection."""
    try:
        embedding = create_embedding(text)
        if embedding:
            collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[item_id]
            )
            return True
    except Exception as e:
        print(f"Error adding item to collection: {e}")
    return False

# Global client variable
CHROMA_CLIENT = get_chroma_client()
CHROMA_COLLECTIONS = setup_collections(CHROMA_CLIENT) if CHROMA_CLIENT else {}