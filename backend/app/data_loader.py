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

from .database import CHROMA_COLLECTIONS, COLLECTION_MYNTRA_CATALOG, COLLECTION_ORDER_HISTORY, COLLECTION_CELEB_STYLES, create_embedding, process_and_add_item

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MOCK_USER_ID = os.getenv("MOCK_USER_ID", "test_user")

# Direct paths - much simpler and more reliable
CELEBRITY_IMAGE_DIR = r"D:\projects\Prism\Stylesense_ai\data\Celeb_FBI_Dataset"
MYNTRA_CATALOG_FILE = r"D:\projects\Prism\Stylesense_ai\data\myntra202305041052.csv"
ORDER_HISTORY_FILE = r"D:\projects\Prism\Stylesense_ai\data\Order_History.csv"

# Configuration
BATCH_SIZE = 50  # Process items in batches
MAX_WORKERS = 4  # Number of concurrent threads for embedding generation
RATE_LIMIT_DELAY = 1.0  # Increased delay to avoid rate limits (1 second between calls)
SKIP_CELEBRITY_IMAGES = False  # Enable celebrity processing with correct path

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
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        # Use current Gemini models (gemini-pro-vision is deprecated as of July 2024)
        model_names = [
            
            'gemini-2.5-flash',  # Newer if available
           
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                
                # Create image part for multimodal input
                image_part = {
                    "mime_type": "image/jpeg",
                    "data": base64_image
                }
                
                prompt = "Describe this fashion style and outfit in detail, focusing on colors, patterns, style, and clothing items."
                
                response = model.generate_content([prompt, image_part])
                if response.text:
                    return response.text
                    
            except Exception as model_error:
                print(f"Model {model_name} failed: {model_error}")
                continue
                
        print("❌ All vision models failed")
        return None
        
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return None

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
        
        if description and not (description.startswith("Error") or description is None):
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

def load_external_datasets():
    """Loads and embeds all static external datasets with optimizations."""
    
    if not CHROMA_COLLECTIONS:
        print("Cannot load data: ChromaDB client is not ready.")
        return

    print("Starting optimized data loading process...")
    
    # Debug: Print all paths to verify they're correct
    print(f"\nPath Verification:")
    print(f"   Celebrity images: {CELEBRITY_IMAGE_DIR}")
    print(f"   Myntra catalog: {MYNTRA_CATALOG_FILE}")
    print(f"   Order history: {ORDER_HISTORY_FILE}")
    print(f"   Celebrity dir exists: {os.path.isdir(CELEBRITY_IMAGE_DIR)}")
    print(f"   Myntra file exists: {os.path.exists(MYNTRA_CATALOG_FILE)}")
    print(f"   Order file exists: {os.path.exists(ORDER_HISTORY_FILE)}")
    
    start_time = time.time()

    # 1. Load Product Catalog (Myntra) with batch processing
    print("\n📦 Loading Myntra Product Catalog...")
    
    # Check if already loaded
    existing_products = check_collection_exists_and_size(COLLECTION_MYNTRA_CATALOG)
    if existing_products > 0:
        print(f"✅ Product catalog already has {existing_products} items. Skipping reload.")
    else:
        try:
            if not os.path.exists(MYNTRA_CATALOG_FILE):
                print(f"❌ Product catalog file not found at {MYNTRA_CATALOG_FILE}")
            else:
                print("📂 Reading product catalog file...")
                product_df = pd.read_csv(MYNTRA_CATALOG_FILE)
                

                if not product_df.empty:
                    print(f"📊 Found {len(product_df)} products in catalog")
                    
                    # Clean data
                    product_df = product_df.dropna(subset=['name', 'seller'])
                    print(f"📊 After cleaning: {len(product_df)} products")
                    
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
                    
                    print(f"✅ Loaded {loaded_count} items into Product Catalog.")
                else:
                    print("⚠️ Product catalog file is empty.")
                    
        except Exception as e:
            print(f"❌ Error loading product catalog: {e}")

    # 2. Load Style Inspiration (Celebrity Images) with parallel processing
    print("\n🌟 Loading Style Inspiration Catalog from images...")
    
    if SKIP_CELEBRITY_IMAGES:
        print("⚠️ Skipping celebrity images due to API issues. Set SKIP_CELEBRITY_IMAGES = False when API is working.")
    else:
        # existing_styles = check_collection_exists_and_size(COLLECTION_CELEB_STYLES)
        # if existing_styles > 0:
        #     print(f"🗑️ Clearing existing {existing_styles} celebrity items to reload with fixed paths...")
        #     try:
        #         # Clear the collection
        #         CHROMA_COLLECTIONS[COLLECTION_CELEB_STYLES].delete(where={})
        #         print("✅ Celebrity collection cleared")
        #     except Exception as e:
        #         print(f"⚠️ Error clearing collection: {e}")
        existing_styles = check_collection_exists_and_size(COLLECTION_CELEB_STYLES)
        if existing_styles > 0:
            print(f"✅ Style Inspiration already has {existing_styles} items. Skipping reload.")
            return
        if os.path.isdir(CELEBRITY_IMAGE_DIR):
            image_paths = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                image_paths.extend(glob.glob(os.path.join(CELEBRITY_IMAGE_DIR, ext)))
            
            if image_paths:
                print(f"📂 Found {len(image_paths)} celebrity images")
                counter = ProgressCounter()
                
                # Process with limited concurrency to avoid API rate limits
                with tqdm(total=len(image_paths), desc="Processing celebrity images", unit="images") as pbar:
                    with ThreadPoolExecutor(max_workers=2) as executor:  # Limited workers for API calls
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
                                result = future.result(timeout=60)  # 60 second timeout
                                loaded_count += result
                                pbar.update(1)
                            except Exception as e:
                                print(f"❌ Error processing celebrity image: {e}")
                                pbar.update(1)
                
                print(f"✅ Loaded {loaded_count} styles into Style Inspiration Catalog.")
            else:
                print(f"⚠️ No image files found in {CELEBRITY_IMAGE_DIR}")
        else:
            print(f"❌ Directory not found: {CELEBRITY_IMAGE_DIR}")

    # 3. Load Order History (Filtered User Data)
    print(f"\n🛍️ Loading Order History for user: {MOCK_USER_ID}")
    
    existing_orders = check_collection_exists_and_size(COLLECTION_ORDER_HISTORY)
    if existing_orders > 0:
        print(f"✅ Order history already has {existing_orders} items. Skipping reload.")
    else:
        try:
            if not os.path.exists(ORDER_HISTORY_FILE):
                print(f"❌ Order history file not found at {ORDER_HISTORY_FILE}")
            else:
                order_df = pd.read_csv(ORDER_HISTORY_FILE)
                
                if not order_df.empty:
                    print(f"📊 Found {len(order_df)} orders in history")
                    
                    # Filter for fashion items
                    FASHION_KEYWORDS = ['Apparel', 'Accessories', 'Footwear', 'Jewelry', 'Bag', 'Clothing']
                    fashion_filter = order_df['Product_Category'].astype(str).str.contains(
                        '|'.join(FASHION_KEYWORDS), case=False, na=False
                    )
                    order_df = order_df[fashion_filter]
                    
                    print(f"📊 After filtering for fashion items: {len(order_df)} orders")
                    
                    if not order_df.empty:
                        order_df['search_text'] = (
                            order_df['Product_Description'].astype(str) + " " + 
                            order_df['Product_Category'].astype(str)
                        )
                        order_df = order_df.dropna(subset=['search_text'])

                        loaded_count = 0
                        with tqdm(total=len(order_df), desc="Processing order history", unit="orders") as pbar:
                            for i, row in order_df.iterrows():
                                try:
                                    embedding = create_embedding(row['search_text'])
                                    if embedding:
                                        CHROMA_COLLECTIONS[COLLECTION_ORDER_HISTORY].add(
                                            embeddings=[embedding],
                                            documents=[row['search_text']],
                                            metadatas=[{
                                                'user_id': MOCK_USER_ID, 
                                                'source': 'order_history_filtered',
                                                'category': str(row['Product_Category'])
                                            }],
                                            ids=[f"order_{i}"]
                                        )
                                        loaded_count += 1
                                    pbar.update(1)
                                except Exception as e:
                                    print(f"Error processing order {i}: {e}")
                                    pbar.update(1)

                        print(f"✅ Loaded {loaded_count} items for '{MOCK_USER_ID}' into Order History.")
                    else:
                        print("⚠️ No fashion items found in order history.")
                else:
                    print("⚠️ Order history file is empty.")
                    
        except Exception as e:
            print(f"❌ Error loading order history: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n🎉 Data Loading Complete! Total time: {duration:.2f} seconds")
    print("✅ Backend is ready to serve queries.")

    # Print final collection sizes
    print("\n📊 Final Collection Sizes:")
    for collection_name in [COLLECTION_MYNTRA_CATALOG, COLLECTION_CELEB_STYLES, COLLECTION_ORDER_HISTORY]:
        size = check_collection_exists_and_size(collection_name)
        print(f"   • {collection_name}: {size} items")

if __name__ == '__main__':
    load_external_datasets()