from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommender import generate_style_recommendation
import os

app = FastAPI(title="StyleSense AI API")

# Pydantic Schemas for Request/Response
class StyleRequest(BaseModel):
    user_id: str
    user_prompt: str
    current_location: str = os.getenv("DEFAULT_LOCATION", "Vellore, India")
    # In a real app, user would upload a photo to get emotion, 
    # but we'll mock emotion for the hackathon
    current_emotion: str = "Neutral"

class StyleRecommendation(BaseModel):
    celebrity_twin: str
    weather_info: str
    final_recommendation: str
    items_owned: list
    items_to_buy: list

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "StyleSense AI Backend is running."}

@app.post("/recommend", response_model=StyleRecommendation)
async def recommend_style(request: StyleRequest):
    """
    Main endpoint for style recommendation.
    Triggers the full Dual-RAG and LLM orchestration.
    """
    print(f"Received request from user: {request.user_id}")
    
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
        raise HTTPException(status_code=500, detail=str(e))

# Note: You would add a separate /upload_wardrobe endpoint here for user data ingestion.