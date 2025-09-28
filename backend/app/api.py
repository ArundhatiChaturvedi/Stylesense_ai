from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import base64
import io
from PIL import Image
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Import from your existing modules
try:
    from .recommender import generate_style_recommendation
except ImportError:
    print("Warning: recommender module not found. Recommendation features will be limited.")
    generate_style_recommendation = None

from .database import (
    add_user_style_item, 
    get_user_style_count, 
    get_user_items_by_source,
    search_user_styles,
    search_products,
    search_celebrity_styles,
    clear_user_styles,
    health_check,
    CHROMA_COLLECTIONS, 
    COLLECTION_USER_STYLES
)
from .data_loader import load_order_history_to_user_styles

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="StyleSense AI API", version="2.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class StyleRequest(BaseModel):
    user_id: str
    user_prompt: str
    current_location: str = os.getenv("DEFAULT_LOCATION", "Mumbai")

class StyleQuery(BaseModel):
    query: str
    user_id: str
    max_results: Optional[int] = 10

class ProductQuery(BaseModel):
    query: str
    max_results: Optional[int] = 10

class UserImageUpload(BaseModel):
    user_id: str
    image_base64: str

class StyleRecommendation(BaseModel):
    celebrity_twin: str
    weather_info: str
    final_recommendation: str
    items_owned: List[Dict[str, Any]]
    items_to_buy: List[Dict[str, Any]]
    extracted_emotion: str

class WardrobeUploadResponse(BaseModel):
    message: str
    items_processed: int
    user_id: str
    total_style_items: int
    wardrobe_items: int

class UserStatusResponse(BaseModel):
    user_exists: bool
    wardrobe_items_count: int
    purchase_history_count: int
    total_items: int
    message: str

# Helper functions
def validate_and_convert_image(image_data: bytes) -> str:
    """Validate and convert image to base64."""
    try:
        # Open image to validate
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (max 1024x1024)
        max_size = (1024, 1024)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

def analyze_wardrobe_image(base64_image: str):
    """Analyze uploaded wardrobe image using Gemini Vision."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": base64_image
        }
        
        prompt = """Describe this clothing item in detail for a fashion wardrobe. Focus on:
        - Type of clothing (shirt, dress, pants, etc.)
        - Color and patterns
        - Style (casual, formal, vintage, etc.)
        - Material/fabric if visible
        - Any distinctive features
        Keep the description concise but comprehensive for fashion matching."""
        
        # Configure safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        response = model.generate_content([prompt, image_part], safety_settings=safety_settings)
        if response.text:
            return response.text.strip()
        return "Clothing item"
        
    except Exception as e:
        print(f"Error analyzing wardrobe image: {e}")
        return "Clothing item"

# --- Endpoints ---

@app.get("/")
def read_root():
    return {
        "message": "StyleSense AI Backend is running.", 
        "version": "2.0.0",
        "features": [
            "User wardrobe management",
            "Purchase history integration", 
            "AI-powered style recommendations",
            "Multi-collection vector search",
            "Image analysis with Gemini Vision"
        ]
    }

@app.get("/health")
def health_check_endpoint():
    """Health check for the API and database connections."""
    health_status = health_check()
    
    if health_status["status"] == "error":
        raise HTTPException(status_code=500, detail=health_status["message"])
    
    return health_status

@app.get("/user/{user_id}/status", response_model=UserStatusResponse)
def check_user_status(user_id: str):
    """Check if user has uploaded wardrobe items and purchase history."""
    try:
        total_items = get_user_style_count(user_id)
        wardrobe_items = len(get_user_items_by_source(user_id, 'wardrobe_upload'))
        purchase_items = len(get_user_items_by_source(user_id, 'purchase_history'))
        
        return UserStatusResponse(
            user_exists=total_items > 0,
            wardrobe_items_count=wardrobe_items,
            purchase_history_count=purchase_items,
            total_items=total_items,
            message=f"User has {total_items} total items ({wardrobe_items} wardrobe, {purchase_items} purchase history)" if total_items > 0 else "User needs to upload wardrobe or load order history"
        )
        
    except Exception as e:
        print(f"Error checking user status: {e}")
        return UserStatusResponse(
            user_exists=False,
            wardrobe_items_count=0,
            purchase_history_count=0,
            total_items=0,
            message="Error checking user status"
        )

@app.post("/user/{user_id}/upload-wardrobe", response_model=WardrobeUploadResponse)
async def upload_wardrobe(
    user_id: str,
    files: List[UploadFile] = File(...),
):
    """Upload multiple wardrobe images for a user."""
    print(f"Received wardrobe upload from user: {user_id}")
    print(f"Number of files: {len(files)}")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Validate file types
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Only JPEG, JPG, PNG allowed."
            )
    
    processed_items = 0
    
    try:
        for i, file in enumerate(files):
            # Read and validate image
            image_content = await file.read()
            
            if len(image_content) > 10 * 1024 * 1024:  # 10MB limit
                print(f"Skipping {file.filename} - too large")
                continue
                
            # Convert and validate image
            base64_image = validate_and_convert_image(image_content)
            
            # Analyze the image
            description = analyze_wardrobe_image(base64_image)
            
            # Store in unified User_Styles collection
            success = add_user_style_item(
                user_id=user_id,
                description=description,
                source_type='wardrobe_upload',
                metadata={'image_filename': file.filename}
            )
            
            if success:
                processed_items += 1
            
            # Small delay to avoid API rate limits
            time.sleep(0.5)
        
        # Get updated counts
        total_items = get_user_style_count(user_id)
        wardrobe_items = len(get_user_items_by_source(user_id, 'wardrobe_upload'))
        
        return WardrobeUploadResponse(
            message=f"Successfully processed {processed_items} out of {len(files)} wardrobe items",
            items_processed=processed_items,
            user_id=user_id,
            total_style_items=total_items,
            wardrobe_items=wardrobe_items
        )
        
    except Exception as e:
        print(f"Error processing wardrobe upload: {e}")
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")

@app.post("/user/styles/upload-base64")
async def upload_user_image_base64(upload_data: UserImageUpload):
    """Upload user's wardrobe image as base64 string."""
    try:
        # Validate base64 string
        try:
            img_data = base64.b64decode(upload_data.image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Validate and convert image
        img_base64 = validate_and_convert_image(img_data)
        
        # Analyze the image
        description = analyze_wardrobe_image(img_base64)
        
        # Add to user's style collection
        success = add_user_style_item(
            user_id=upload_data.user_id,
            description=description,
            source_type='wardrobe_upload',
            metadata={'upload_method': 'base64'}
        )
        
        if success:
            # Get updated count
            total_items = get_user_style_count(upload_data.user_id)
            wardrobe_items = len(get_user_items_by_source(upload_data.user_id, 'wardrobe_upload'))
            
            return {
                "success": True,
                "message": "Image processed and added to your wardrobe",
                "user_id": upload_data.user_id,
                "total_style_items": total_items,
                "wardrobe_items": wardrobe_items,
                "description": description[:100] + "..." if len(description) > 100 else description
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process and store image")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/user/styles/load-orders")
async def load_user_order_history(user_id: str = Form(...)):
    """Load user's order history into their style collection."""
    try:
        loaded_count = load_order_history_to_user_styles(user_id)
        
        if loaded_count > 0:
            return {
                "success": True,
                "message": f"Loaded {loaded_count} items from order history",
                "user_id": user_id,
                "items_loaded": loaded_count
            }
        else:
            return {
                "success": False,
                "message": "No new order history items to load (may already exist)",
                "user_id": user_id,
                "items_loaded": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading order history: {str(e)}")

@app.post("/user/styles/search")
async def search_user_styles_endpoint(query: StyleQuery):
    """Search through user's personal style items (wardrobe + purchase history)."""
    try:
        results = search_user_styles(query.user_id, query.query, query.max_results)
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return {"results": [], "message": "No matching styles found", "user_id": query.user_id}
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "description": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "similarity_score": 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return {
            "results": formatted_results,
            "total_found": len(formatted_results),
            "user_id": query.user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching user styles: {str(e)}")

@app.post("/products/search")
async def search_products_endpoint(query: ProductQuery):
    """Search through product catalog."""
    try:
        results = search_products(query.query, query.max_results)
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return {"results": [], "message": "No matching products found"}
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "description": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "similarity_score": 1 - results['distances'][0][i]
            })
        
        return {
            "results": formatted_results,
            "total_found": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

@app.post("/celebrity-styles/search")
async def search_celebrity_styles_endpoint(query: ProductQuery):
    """Search through celebrity style inspiration."""
    try:
        results = search_celebrity_styles(query.query, query.max_results)
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return {"results": [], "message": "No matching celebrity styles found"}
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "description": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "similarity_score": 1 - results['distances'][0][i]
            })
        
        return {
            "results": formatted_results,
            "total_found": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching celebrity styles: {str(e)}")

@app.post("/recommend/outfit")
async def get_outfit_recommendations(query: StyleQuery):
    """Get personalized outfit recommendations based on user's style and available products."""
    try:
        # Search user's personal styles
        user_styles = search_user_styles(query.user_id, query.query, 5)
        
        # Search product catalog
        products = search_products(query.query, query.max_results)
        
        # Search celebrity inspiration
        celebrity_styles = search_celebrity_styles(query.query, 3)
        
        return {
            "query": query.query,
            "user_id": query.user_id,
            "recommendations": {
                "matching_user_styles": user_styles.get('documents', [[]])[0] if user_styles else [],
                "suggested_products": products.get('documents', [[]])[0] if products else [],
                "style_inspiration": celebrity_styles.get('documents', [[]])[0] if celebrity_styles else []
            },
            "personalization_data": {
                "user_style_count": get_user_style_count(query.user_id),
                "wardrobe_items": len(get_user_items_by_source(query.user_id, 'wardrobe_upload')),
                "purchase_history_items": len(get_user_items_by_source(query.user_id, 'purchase_history'))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.post("/recommend", response_model=StyleRecommendation)
async def recommend_style(request: StyleRequest):
    """
    Main endpoint for style recommendation using the recommender module.
    Requires user to have uploaded wardrobe or have purchase history.
    """
    if not generate_style_recommendation:
        raise HTTPException(status_code=501, detail="Style recommendation feature not available. Use /recommend/outfit instead.")
    
    print(f"Received recommendation request from user: {request.user_id}")
    print(f"User prompt: {request.user_prompt}")
    
    # Check if user has style items
    user_status = check_user_status(request.user_id)
    if not user_status.user_exists:
        raise HTTPException(
            status_code=400,
            detail="User must upload wardrobe items or load order history before getting recommendations. Use /user/{user_id}/upload-wardrobe or /user/styles/load-orders endpoint first."
        )
    
    try:
        recommendation_data = generate_style_recommendation(
            user_id=request.user_id,
            user_prompt=request.user_prompt,
            location=request.current_location
        )
        
        return StyleRecommendation(**recommendation_data)

    except Exception as e:
        print(f"Error during recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.get("/user/{user_id}/styles/stats")
async def get_user_style_stats(user_id: str):
    """Get statistics about user's style items."""
    try:
        total_items = get_user_style_count(user_id)
        wardrobe_items = len(get_user_items_by_source(user_id, 'wardrobe_upload'))
        purchase_items = len(get_user_items_by_source(user_id, 'purchase_history'))
        
        return {
            "user_id": user_id,
            "total_style_items": total_items,
            "wardrobe_uploads": wardrobe_items,
            "purchase_history": purchase_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

@app.delete("/user/{user_id}/wardrobe")
def clear_user_wardrobe(user_id: str, source_type: Optional[str] = None):
    """Clear all user style items or specific source type (for testing/reset)."""
    try:
        success = clear_user_styles(user_id, source_type)
        
        if success:
            remaining_items = get_user_style_count(user_id)
            return {
                "message": f"Cleared user style items" + (f" of type {source_type}" if source_type else ""),
                "user_id": user_id,
                "remaining_items": remaining_items
            }
        else:
            return {
                "message": f"No items found to clear for user {user_id}" + (f" with source {source_type}" if source_type else ""),
                "user_id": user_id
            }
            
    except Exception as e:
        print(f"Error clearing wardrobe: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear wardrobe: {str(e)}")

@app.get("/collections/status")
def get_collections_status():
    """Get status of all ChromaDB collections."""
    try:
        from .database import get_collection_stats
        stats = get_collection_stats()
        return {"collections": stats, "status": "healthy"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)