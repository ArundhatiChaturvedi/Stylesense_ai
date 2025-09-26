import chromadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# ChromaDB Collection Names (The "Drawers" in your filing cabinet)
COLLECTION_USER_WARDROBE = "user_wardrobe"
COLLECTION_PRODUCT_CATALOG = "product_catalog"
COLLECTION_STYLE_INSPIRATION = "style_inspiration"

def get_chroma_client():
    """Returns the HTTP client to connect to the dedicated ChromaDB server."""
    # Note: The ChromaDB server must be running separately (e.g., using 'chroma run')
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # Check connection by listing collections (throws error if connection fails)
        client.list_collections() 
        return client
    except Exception as e:
        print(f"Error connecting to ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT}. Ensure the server is running.")
        print(f"Error details: {e}")
        return None

def setup_collections(client):
    """Creates the necessary collections if they don't exist."""
    collections = {}
    collections[COLLECTION_USER_WARDROBE] = client.get_or_create_collection(name=COLLECTION_USER_WARDROBE)
    collections[COLLECTION_PRODUCT_CATALOG] = client.get_or_create_collection(name=COLLECTION_PRODUCT_CATALOG)
    collections[COLLECTION_STYLE_INSPIRATION] = client.get_or_create_collection(name=COLLECTION_STYLE_INSPIRATION)
    print("ChromaDB collections verified/created successfully.")
    return collections

# Global client variable
CHROMA_CLIENT = get_chroma_client()
CHROMA_COLLECTIONS = setup_collections(CHROMA_CLIENT) if CHROMA_CLIENT else {}