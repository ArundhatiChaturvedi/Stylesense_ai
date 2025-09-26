import pandas as pd
import os
from database import CHROMA_COLLECTIONS, COLLECTION_PRODUCT_CATALOG, COLLECTION_STYLE_INSPIRATION
from sentence_transformers import SentenceTransformer

# Load the embedding model (runs locally)
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2') 

def create_embedding(text):
    """Generates a vector embedding for a piece of text."""
    # Check if text is valid before embedding
    if pd.isna(text) or not isinstance(text, str):
        return None
    return EMBEDDING_MODEL.encode(text).tolist()

def load_external_datasets():
    """Loads and embeds all static external datasets into ChromaDB."""
    
    # 1. Load Product Catalog (Myntra/Kaggle)
    print("Loading Product Catalog...")
    product_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/myntra_catalog.csv'))
    # Clean data, e.g., combine Name and Description
    product_df['search_text'] = product_df['ProductName'] + " " + product_df.get('Description', '')

    product_embeddings = product_df['search_text'].apply(create_embedding).tolist()
    product_df = product_df[product_df['search_text'].apply(lambda x: x is not None)] # Remove rows that failed embedding

    # Add to ChromaDB
    CHROMA_COLLECTIONS[COLLECTION_PRODUCT_CATALOG].add(
        embeddings=[e for e in product_embeddings if e is not None],
        documents=product_df['search_text'].tolist(),
        metadatas=[{'brand': b} for b in product_df['ProductBrand'].tolist()],
        ids=[f"prod_{i}" for i in range(len(product_df))]
    )
    print(f"Loaded {len(product_df)} items into Product Catalog.")

    # 2. Load Style Inspiration (Celebrity)
    print("Loading Style Inspiration Catalog...")
    # NOTE: You need to create this CSV yourself with columns: Name, StyleDescription, ImageURL
    style_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/celebrity_styles.csv'))
    
    style_embeddings = style_df['StyleDescription'].apply(create_embedding).tolist()
    style_df = style_df[style_df['StyleDescription'].apply(lambda x: x is not None)]

    # Add to ChromaDB
    CHROMA_COLLECTIONS[COLLECTION_STYLE_INSPIRATION].add(
        embeddings=[e for e in style_embeddings if e is not None],
        documents=style_df['StyleDescription'].tolist(),
        metadatas=[{'celebrity': c} for c in style_df['Name'].tolist()],
        ids=[f"twin_{i}" for i in range(len(style_df))]
    )
    print(f"Loaded {len(style_df)} styles into Style Inspiration Catalog.")

    # 3. Load Order History (This is a simplified version of Step 1 for user data)
    print("Loading Initial Order History (Mock User Data)...")
    # For a working demo, you will load this data and tag it for a mock user (e.g., 'test_user')
    order_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/shopping_history.csv'))
    order_df['search_text'] = order_df['Description'] + " " + order_df.get('Category', '')
    
    order_embeddings = order_df['search_text'].apply(create_embedding).tolist()
    order_df = order_df[order_df['search_text'].apply(lambda x: x is not None)]

    # Add to User Wardrobe Collection with a mock user ID
    CHROMA_COLLECTIONS[COLLECTION_USER_WARDROBE].add(
        embeddings=[e for e in order_embeddings if e is not None],
        documents=order_df['search_text'].tolist(),
        metadatas=[{'user_id': 'test_user', 'source': 'order_history'} for _ in range(len(order_df))],
        ids=[f"order_{i}" for i in range(len(order_df))]
    )
    print(f"Loaded {len(order_df)} items for 'test_user' into User Wardrobe.")


if __name__ == '__main__':
    # ONLY run this once to populate your database!
    load_external_datasets()