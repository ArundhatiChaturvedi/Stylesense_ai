import pandas as pd
import os
import glob
import base64
from PIL import Image 
from dotenv import load_dotenv
import google.generativeai as genai
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# FIXED IMPORTS - using unified collection names
from .database import CHROMA_COLLECTIONS, COLLECTION_MYNTRA_CATALOG, COLLECTION_USER_STYLES, COLLECTION_CELEB_STYLES, create_embedding, add_user_style_item

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MOCK_USER_ID = os.getenv("MOCK_USER_ID", "test_user")

# Get the absolute path to the project root - fixed for your structure
if __name__ == '__main__':
    # When run directly, use current directory structure
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
else:
    # When imported as module, go up one level from app directory
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Use the exact paths from your directory structure
CELEBRITY_IMAGE_DIR = os.path.join(DATA_DIR, "Celeb_FBI_Dataset")
MYNTRA_CATALOG_FILE = os.path.join(DATA_DIR, "myntra202305041052.csv")
ORDER_HISTORY_FILE = os.path.join(DATA_DIR, "Order_History.csv")

# Configuration
BATCH_SIZE = 50
MAX_WORKERS = 4
RATE_LIMIT_DELAY = 1.0
SKIP_CELEBRITY_IMAGES = False

# Thread-safe counter for progress tracking
class ProgressCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    @property
    def value(self):
        with self._lock:
            return self._value

def image_to_base64(image_path):
    """Converts a local image file to a base64 string for the Gemini Vision API."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def analyze_uploaded_image_vision(base64_image):
    """Analyze image using current Gemini Vision models."""
    try:
        time.sleep(RATE_LIMIT_DELAY)
        
        model_names = ['gemini-2.5-flash']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                
                image_part = {
                    "mime_type": "image/jpeg",
                    "data": base64_image
                }
                
                prompt = "Describe this fashion style and outfit in detail, focusing on colors, patterns, style, and clothing items."
                
                # Configure safety settings
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
                
                response = model.generate_content([prompt, image_part], safety_settings=safety_settings)
                
                if response.text:
                    return response.text
                    
            except Exception as model_error:
                error_msg = str(model_error)
                if "PROHIBITED_CONTENT" in error_msg or "block_reason" in error_msg:
                    print(f"Content blocked for safety - skipping this image")
                    return None
                elif "429" in error_msg or "quota" in error_msg.lower():
                    print(f"API quota exceeded - skipping remaining images")
                    return None
                else:
                    print(f"Model {model_name} failed: {model_error}")
                    continue
                
        return None
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None

def create_sample_order_history(file_path):
    """Create sample order history data if file doesn't exist."""
    print("Creating sample Order_History.csv with fashion items...")
    
    sample_orders = [
        {"Product_Description": "Navy Blue Formal Blazer", "Product_Category": "Apparel"},
        {"Product_Description": "White Cotton Dress Shirt", "Product_Category": "Apparel"},
        {"Product_Description": "Black Leather Oxford Shoes", "Product_Category": "Footwear"},
        {"Product_Description": "Dark Wash Denim Jeans", "Product_Category": "Apparel"},
        {"Product_Description": "Red Silk Blouse", "Product_Category": "Apparel"},
        {"Product_Description": "Brown Leather Belt", "Product_Category": "Accessories"},
        {"Product_Description": "Black Evening Dress", "Product_Category": "Apparel"},
        {"Product_Description": "White Canvas Sneakers", "Product_Category": "Footwear"},
        {"Product_Description": "Gold Statement Necklace", "Product_Category": "Jewelry"},
        {"Product_Description": "Casual Gray T-shirt", "Product_Category": "Apparel"},
        {"Product_Description": "Blue Denim Jacket", "Product_Category": "Apparel"},
        {"Product_Description": "Black Leather Handbag", "Product_Category": "Bag"},
        {"Product_Description": "Striped Cotton Cardigan", "Product_Category": "Apparel"},
        {"Product_Description": "Brown Suede Ankle Boots", "Product_Category": "Footwear"},
        {"Product_Description": "Silver Bracelet", "Product_Category": "Jewelry"},
        {"Product_Description": "Floral Print Midi Dress", "Product_Category": "Apparel"},
        {"Product_Description": "Wool Blend Coat", "Product_Category": "Apparel"},
        {"Product_Description": "White Sports Shoes", "Product_Category": "Footwear"},
        {"Product_Description": "Leather Crossbody Bag", "Product_Category": "Bag"},
        {"Product_Description": "Plaid Button-down Shirt", "Product_Category": "Apparel"}
    ]
    
    df = pd.DataFrame(sample_orders)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    print(f"Created sample order history with {len(sample_orders)} fashion items at {file_path}")

def process_product_batch(batch_data, collection, counter, pbar):
    """Process a batch of products and add them to ChromaDB."""
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []
    batch_ids = []
    
    for i, (idx, row) in enumerate(batch_data):
        try:
            search_text = str(row['name']) + " by " + str(row['seller'])
            if pd.isna(search_text) or search_text.strip() == "":
                continue
                
            embedding = create_embedding(search_text)
            if embedding:
                batch_embeddings.append(embedding)
                batch_documents.append(search_text)
                batch_metadatas.append({
                    'brand': str(row['seller']),
                    'link': str(row.get('purl', '')),
                    'name': str(row['name'])
                })
                batch_ids.append(f"prod_{idx}")
                
        except Exception as e:
            print(f"Error processing product at index {idx}: {e}")
            continue
    
    # Batch insert to ChromaDB
    if batch_embeddings:
        try:
            collection.add(
                embeddings=batch_embeddings,
                documents=batch_documents,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            counter.increment()
            pbar.update(len(batch_embeddings))
            return len(batch_embeddings)
        except Exception as e:
            print(f"Error adding batch to ChromaDB: {e}")
            return 0
    
    return 0

def process_celebrity_image(image_path, collection, counter, celebrity_idx):
    """Process a single celebrity image."""
    try:
        base64_data = image_to_base64(image_path)
        if not base64_data:
            return 0
            
        description = analyze_uploaded_image_vision(base64_data)
        
        if description and description.strip():
            embedding = create_embedding(description)
            if embedding:
                celebrity_name = os.path.splitext(os.path.basename(image_path))[0]
                
                collection.add(
                    embeddings=[embedding],
                    documents=[description],
                    metadatas=[{
                        'celebrity': celebrity_name, 
                        'image_url': f"local://{image_path}",
                        'description': description[:200] + "..." if len(description) > 200 else description
                    }],
                    ids=[f"celeb_{celebrity_name}_{celebrity_idx}"]
                )
                counter.increment()
                return 1
                
    except Exception as e:
        print(f"Error processing celebrity image {image_path}: {e}")
        
    return 0

def check_collection_exists_and_size(collection_name):
    """Check if collection exists and return its size."""
    try:
        if collection_name in CHROMA_COLLECTIONS:
            collection = CHROMA_COLLECTIONS[collection_name]
            count = collection.count()
            return count
        return 0
    except Exception as e:
        print(f"Error checking collection {collection_name}: {e}")
        return 0

def get_user_orders_count(user_id):
    """Get count of existing user order history items."""
    try:
        if COLLECTION_USER_STYLES not in CHROMA_COLLECTIONS:
            return 0
        collection = CHROMA_COLLECTIONS[COLLECTION_USER_STYLES]
        
        # Fix: Use $and operator for multiple conditions in ChromaDB
        where_clause = {
            "$and": [
                {"user_id": user_id},
                {"source": "purchase_history"}
            ]
        }
        
        results = collection.get(where=where_clause)
        return len(results['ids']) if results['ids'] else 0
    except Exception as e:
        print(f"Error getting user orders count: {e}")
        # Fallback: try getting all user items and filter manually
        try:
            all_user_results = collection.get(where={"user_id": user_id})
            if all_user_results['metadatas']:
                purchase_history_count = sum(
                    1 for metadata in all_user_results['metadatas'] 
                    if metadata.get('source') == 'purchase_history'
                )
                return purchase_history_count
        except Exception as e2:
            print(f"Fallback method also failed: {e2}")
        return 0

def load_order_history_to_user_styles(user_id):
    """Load order history into User_Styles collection for the specified user."""
    print(f"Loading Order History into User_Styles Collection for user: {user_id}")
    
    # Check if order history is already loaded for this user
    existing_orders = get_user_orders_count(user_id)
    if existing_orders > 0:
        print(f"User '{user_id}' already has {existing_orders} order history items. Skipping reload.")
        return existing_orders
    
    try:
        # Check if the actual file exists first
        print(f"Looking for Order History file at: {ORDER_HISTORY_FILE}")
        print(f"File exists: {os.path.exists(ORDER_HISTORY_FILE)}")
        print(f"File is file: {os.path.isfile(ORDER_HISTORY_FILE)}")
        
        # Create sample order history if file doesn't exist
        if not os.path.exists(ORDER_HISTORY_FILE):
            print(f"Order history file not found. Creating sample data...")
            create_sample_order_history(ORDER_HISTORY_FILE)
        
        # Now try to load the file
        if os.path.exists(ORDER_HISTORY_FILE):
            print(f"Reading order history file...")
            order_df = pd.read_csv(ORDER_HISTORY_FILE)
            
            if not order_df.empty:
                print(f"Found {len(order_df)} orders in history")
                
                # Filter for fashion items
                FASHION_KEYWORDS = ['Apparel', 'Accessories', 'Footwear', 'Jewelry', 'Bag', 'Clothing']
                
                # Handle the case where Product_Category might not exist
                if 'Product_Category' not in order_df.columns:
                    print("Product_Category column not found. Adding default category.")
                    order_df['Product_Category'] = 'Apparel'
                
                fashion_filter = order_df['Product_Category'].astype(str).str.contains(
                    '|'.join(FASHION_KEYWORDS), case=False, na=False
                )
                order_df = order_df[fashion_filter]
                
                print(f"After filtering for fashion items: {len(order_df)} orders")
                
                if not order_df.empty:
                    # Create search text for embedding
                    if 'Product_Description' in order_df.columns:
                        order_df['search_text'] = (
                            order_df['Product_Description'].astype(str) + " " + 
                            order_df['Product_Category'].astype(str)
                        )
                    else:
                        # Fallback if Product_Description doesn't exist
                        order_df['search_text'] = order_df['Product_Category'].astype(str)
                    
                    order_df = order_df.dropna(subset=['search_text'])

                    loaded_count = 0
                    with tqdm(total=len(order_df), desc="Processing order history into User_Styles", unit="orders") as pbar:
                        for i, row in order_df.iterrows():
                            try:
                                # USE THE UNIFIED add_user_style_item FUNCTION
                                success = add_user_style_item(
                                    user_id=user_id,
                                    description=row['search_text'],
                                    source_type='purchase_history',
                                    metadata={'category': str(row['Product_Category'])}
                                )
                                if success:
                                    loaded_count += 1
                                pbar.update(1)
                            except Exception as e:
                                print(f"Error processing order {i}: {e}")
                                pbar.update(1)

                    print(f"Loaded {loaded_count} order history items for '{user_id}' into User_Styles Collection.")
                    return loaded_count
                else:
                    print("No fashion items found in order history.")
                    return 0
            else:
                print("Order history file is empty.")
                return 0
        else:
            print("Could not create or find order history file.")
            return 0
                
    except Exception as e:
        print(f"Error loading order history: {e}")
        return 0

def add_user_wardrobe_image(user_id, image_path_or_base64, is_base64=False):
    """Add user's wardrobe image to User_Styles collection."""
    try:
        if is_base64:
            # Image data is already in base64 format
            base64_data = image_path_or_base64
        else:
            # Convert image file to base64
            base64_data = image_to_base64(image_path_or_base64)
            
        if not base64_data:
            print("Failed to process image data")
            return False
            
        # Analyze the image using Gemini Vision
        description = analyze_uploaded_image_vision(base64_data)
        
        if description and description.strip():
            # Add to User_Styles collection
            success = add_user_style_item(
                user_id=user_id,
                description=description,
                source_type='wardrobe_upload',
                metadata={
                    'image_processed': True,
                    'description_length': len(description)
                }
            )
            
            if success:
                print(f"Successfully added wardrobe image for user '{user_id}'")
                return True
            else:
                print(f"Failed to add wardrobe image to collection")
                return False
        else:
            print("Failed to analyze image or empty description")
            return False
            
    except Exception as e:
        print(f"Error adding user wardrobe image: {e}")
        return False

def load_external_datasets():
    """Loads and embeds all static external datasets with optimizations."""
    
    if not CHROMA_COLLECTIONS:
        print("Cannot load data: ChromaDB client is not ready.")
        return

    print("Starting optimized data loading process...")
    
    # Debug: Print all paths to verify they're correct
    print(f"\nPath Verification:")
    print(f"   Project Root: {PROJECT_ROOT}")
    print(f"   Data Directory: {DATA_DIR}")
    print(f"   Celebrity images: {CELEBRITY_IMAGE_DIR}")
    print(f"   Myntra catalog: {MYNTRA_CATALOG_FILE}")
    print(f"   Order history: {ORDER_HISTORY_FILE}")
    print(f"   Data dir exists: {os.path.isdir(DATA_DIR)}")
    print(f"   Celebrity dir exists: {os.path.isdir(CELEBRITY_IMAGE_DIR)}")
    print(f"   Myntra file exists: {os.path.exists(MYNTRA_CATALOG_FILE)}")
    print(f"   Order file exists: {os.path.exists(ORDER_HISTORY_FILE)}")
    
    start_time = time.time()

    # 1. Load Product Catalog (Myntra) with batch processing
    print(f"\nLoading Myntra Product Catalog...")
    
    existing_products = check_collection_exists_and_size(COLLECTION_MYNTRA_CATALOG)
    if existing_products > 0:
        print(f"Product catalog already has {existing_products} items. Skipping reload.")
    else:
        try:
            if not os.path.exists(MYNTRA_CATALOG_FILE):
                print(f"Product catalog file not found at {MYNTRA_CATALOG_FILE}")
            else:
                print("Reading product catalog file...")
                product_df = pd.read_csv(MYNTRA_CATALOG_FILE)
                
                if not product_df.empty:
                    print(f"Found {len(product_df)} products in catalog")
                    
                    # Clean data
                    product_df = product_df.dropna(subset=['name', 'seller'])
                    print(f"After cleaning: {len(product_df)} products")
                    
                    # Process in batches with progress bar
                    counter = ProgressCounter()
                    batch_data = []
                    loaded_count = 0
                    
                    with tqdm(total=len(product_df), desc="Processing products", unit="items") as pbar:
                        for idx, row in product_df.iterrows():
                            batch_data.append((idx, row))
                            
                            if len(batch_data) >= BATCH_SIZE:
                                loaded_count += process_product_batch(
                                    batch_data, 
                                    CHROMA_COLLECTIONS[COLLECTION_MYNTRA_CATALOG],
                                    counter,
                                    pbar
                                )
                                batch_data = []
                        
                        # Process remaining items
                        if batch_data:
                            loaded_count += process_product_batch(
                                batch_data,
                                CHROMA_COLLECTIONS[COLLECTION_MYNTRA_CATALOG],
                                counter,
                                pbar
                            )
                    
                    print(f"Loaded {loaded_count} items into Product Catalog.")
                else:
                    print("Product catalog file is empty.")
                    
        except Exception as e:
            print(f"Error loading product catalog: {e}")

    # 2. Load Style Inspiration (Celebrity Images)
    print(f"\nLoading Style Inspiration Catalog from images...")
    
    if SKIP_CELEBRITY_IMAGES:
        print("Skipping celebrity images due to configuration.")
    else:
        existing_styles = check_collection_exists_and_size(COLLECTION_CELEB_STYLES)
        if existing_styles > 0:
            print(f"Style Inspiration already has {existing_styles} items. Skipping reload.")
        else:
            if os.path.isdir(CELEBRITY_IMAGE_DIR):
                image_paths = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                    image_paths.extend(glob.glob(os.path.join(CELEBRITY_IMAGE_DIR, ext)))
                
                if image_paths:
                    print(f"Found {len(image_paths)} celebrity images")
                    counter = ProgressCounter()
                    
                    # Process with limited concurrency to avoid API rate limits
                    with tqdm(total=len(image_paths), desc="Processing celebrity images", unit="images") as pbar:
                        with ThreadPoolExecutor(max_workers=2) as executor:
                            futures = []
                            
                            for i, path in enumerate(image_paths):
                                future = executor.submit(
                                    process_celebrity_image,
                                    path,
                                    CHROMA_COLLECTIONS[COLLECTION_CELEB_STYLES],
                                    counter,
                                    i
                                )
                                futures.append(future)
                            
                            loaded_count = 0
                            for future in as_completed(futures):
                                try:
                                    result = future.result(timeout=60)
                                    loaded_count += result
                                    pbar.update(1)
                                except Exception as e:
                                    print(f"Error processing celebrity image: {e}")
                                    pbar.update(1)
                    
                    print(f"Loaded {loaded_count} styles into Style Inspiration Catalog.")
                else:
                    print(f"No image files found in {CELEBRITY_IMAGE_DIR}")
            else:
                print(f"Directory not found: {CELEBRITY_IMAGE_DIR}")

    # 3. Load Order History into User Styles Collection (ALWAYS LOAD FOR DEFAULT USER)
    load_order_history_to_user_styles(MOCK_USER_ID)
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nData Loading Complete! Total time: {duration:.2f} seconds")
    print("Backend is ready to serve queries.")

    # Print final collection sizes
    print(f"\nFinal Collection Sizes:")
    for collection_name in [COLLECTION_MYNTRA_CATALOG, COLLECTION_CELEB_STYLES, COLLECTION_USER_STYLES]:
        size = check_collection_exists_and_size(collection_name)
        print(f"   • {collection_name}: {size} items")

if __name__ == '__main__':
    load_external_datasets()