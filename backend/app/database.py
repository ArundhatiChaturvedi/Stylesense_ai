import chromadb
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import uuid

# Load environment variables
load_dotenv()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# Initialize embedding model
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# ChromaDB Collection Names - 3 collections total
COLLECTION_USER_STYLES = "User_Styles"  # Combined: Order history + uploaded wardrobe
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
    if not client:
        return {}
    collections = {}
    collections[COLLECTION_USER_STYLES] = client.get_or_create_collection(name=COLLECTION_USER_STYLES)
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

def get_user_orders_count(user_id):
    """Get count of existing user order history items."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return 0
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        
        # Get all user items and count purchase_history manually
        results = collection.get(where={"user_id": user_id})
        
        if not results['metadatas']:
            return 0
            
        purchase_history_count = sum(
            1 for metadata in results['metadatas'] 
            if metadata.get('source') == 'purchase_history'
        )
        return purchase_history_count
        
    except Exception as e:
        print(f"Error getting user orders count: {e}")
        return 0

def add_user_style_item(user_id: str, description: str, source_type: str, metadata: dict = None):
    """Add a user's style item to the unified collection."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            print(f"User_Styles collection not available in CHROMA_COLLECTIONS")
            return False
            
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        embedding = create_embedding(description)
        
        if not embedding:
            print(f"Failed to create embedding for description: {description[:100]}...")
            return False
        
        # Create metadata with user_id and source type
        item_metadata = {
            'user_id': user_id,
            'source': source_type,  # 'wardrobe_upload' or 'purchase_history'
        }
        
        # Add additional metadata if provided
        if metadata:
            item_metadata.update(metadata)
        
        # Generate unique ID using UUID to avoid conflicts
        unique_id = str(uuid.uuid4())
        item_id = f"{user_id}_{source_type}_{unique_id}"
        
        collection.add(
            embeddings=[embedding],
            documents=[description],
            metadatas=[item_metadata],
            ids=[item_id]
        )
        
        return True
        
    except Exception as e:
        print(f"Error adding user style item: {e}")
        print(f"User ID: {user_id}, Source: {source_type}")
        print(f"Description: {description[:100]}...")
        return False

def get_user_style_count(user_id: str):
    """Get count of user's style items."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return 0
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        results = collection.get(where={"user_id": user_id})
        return len(results['ids']) if results['ids'] else 0
    except Exception as e:
        print(f"Error getting user style count: {e}")
        return 0

def get_user_items_by_source(user_id: str, source_type: str):
    """Get user's items filtered by source type."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return []
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        
        # Get all user items first, then filter by source
        results = collection.get(where={"user_id": user_id})
        
        if not results['ids']:
            return []
            
        # Filter by source type manually if needed
        filtered_ids = []
        if results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                if metadata.get('source') == source_type:
                    filtered_ids.append(results['ids'][i])
        
        return filtered_ids
        
    except Exception as e:
        print(f"Error getting user items by source: {e}")
        return []

def search_user_styles(user_id: str, query: str, n_results: int = 10):
    """Search through user's style items."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return []
        
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        query_embedding = create_embedding(query)
        
        if not query_embedding:
            return []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            where={"user_id": user_id},
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
        
    except Exception as e:
        print(f"Error searching user styles: {e}")
        return []

def search_products(query: str, n_results: int = 10):
    """Search through product catalog."""
    try:
        if COLLECTION_MYNTRA_CATALOG not in CHROMA_COLLECTIONS:
            return []
        
        collection = CHROMA_COLLECTIONS[COLLECTION_MYNTRA_CATALOG]
        query_embedding = create_embedding(query)
        
        if not query_embedding:
            return []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
        
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

def search_celebrity_styles(query: str, n_results: int = 10):
    """Search through celebrity style inspiration."""
    try:
        if COLLECTION_CELEB_STYLES not in CHROMA_COLLECTIONS:
            return []
        
        collection = CHROMA_COLLECTIONS[COLLECTION_CELEB_STYLES]
        query_embedding = create_embedding(query)
        
        if not query_embedding:
            return []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
        
    except Exception as e:
        print(f"Error searching celebrity styles: {e}")
        return []

def remove_user_style_item(user_id: str, item_id: str):
    """Remove a specific user style item."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return False
        
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        
        # First verify the item belongs to the user
        existing_item = collection.get(ids=[item_id])
        
        if not existing_item['ids'] or len(existing_item['ids']) == 0:
            print(f"Item {item_id} not found")
            return False
            
        # Check if item belongs to the user
        if existing_item['metadatas'][0]['user_id'] != user_id:
            print(f"Item {item_id} does not belong to user {user_id}")
            return False
        
        # Remove the item
        collection.delete(ids=[item_id])
        return True
        
    except Exception as e:
        print(f"Error removing user style item: {e}")
        return False

def clear_user_styles(user_id: str, source_type: str = None):
    """Clear all user style items or items of specific source type."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return False
        
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        
        # Build where clause
        where_clause = {"user_id": user_id}
        if source_type:
            where_clause["source"] = source_type
        
        # Get all matching items
        results = collection.get(where=where_clause)
        
        if results['ids'] and len(results['ids']) > 0:
            # Delete all matching items
            collection.delete(ids=results['ids'])
            print(f"Cleared {len(results['ids'])} items for user {user_id}" + (f" with source {source_type}" if source_type else ""))
            return True
        else:
            print(f"No items found to clear for user {user_id}" + (f" with source {source_type}" if source_type else ""))
            return False
            
    except Exception as e:
        print(f"Error clearing user styles: {e}")
        return False

def get_collection_stats():
    """Get statistics for all collections."""
    stats = {}
    try:
        for collection_name, collection in CHROMA_COLLECTIONS.items():
            try:
                count = collection.count()
                stats[collection_name] = count
            except Exception as e:
                print(f"Error getting stats for {collection_name}: {e}")
                stats[collection_name] = 0
    except Exception as e:
        print(f"Error getting collection stats: {e}")
    
    return stats

def health_check():
    """Check the health of ChromaDB connections and collections."""
    try:
        if not CHROMA_CLIENT:
            return {"status": "error", "message": "ChromaDB client not connected"}
        
        # Test connection
        collections_list = CHROMA_CLIENT.list_collections()
        
        # Get collection stats
        stats = get_collection_stats()
        
        return {
            "status": "healthy",
            "collections": len(CHROMA_COLLECTIONS),
            "stats": stats,
            "client_connected": True
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {e}"}

# Global client variable
CHROMA_CLIENT = get_chroma_client()
CHROMA_COLLECTIONS = setup_collections(CHROMA_CLIENT) if CHROMA_CLIENT else {}