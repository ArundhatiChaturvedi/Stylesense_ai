from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from .recommender import generate_style_recommendation  # Add the dot here
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StyleSense AI API", version="1.0.0")

# ...rest of your code remains the same...

# Pydantic Schemas for Request/Response
class StyleRequest(BaseModel):
    user_id: str
    user_prompt: str
    current_location: str = os.getenv("DEFAULT_LOCATION", "India")
    # In a real app, user would upload a photo to get emotion, 
    # but we'll mock emotion for the hackathon
    current_emotion: str = "Neutral"

class StyleRecommendation(BaseModel):
    celebrity_twin: str
    weather_info: str
    final_recommendation: str
    items_owned: List[Dict[str, Any]]
    items_to_buy: List[Dict[str, Any]]

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "StyleSense AI Backend is running.", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is operational"}

@app.post("/recommend", response_model=StyleRecommendation)
async def recommend_style(request: StyleRequest):
    """
    Main endpoint for style recommendation.
    Triggers the full Dual-RAG and LLM orchestration.
    """
    print(f"Received request from user: {request.user_id}")
    print(f"Prompt: {request.user_prompt}")
    print(f"Location: {request.current_location}")
    
    try:
        recommendation_data = generate_style_recommendation(
            user_id=request.user_id,
            user_prompt=request.user_prompt,
            location=request.current_location,
            emotion=request.current_emotion
        )
        
        return StyleRecommendation(**recommendation_data)

    except Exception as e:
        print(f"Error during recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

# Note: You would add a separate /upload_wardrobe endpoint here for user data ingestion.