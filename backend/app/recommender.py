import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from .database import CHROMA_COLLECTIONS, COLLECTION_MYNTRA_CATALOG, COLLECTION_ORDER_HISTORY, COLLECTION_CELEB_STYLES, create_embedding
from sentence_transformers import SentenceTransformer

# --- Setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
GENERATIVE_MODEL = genai.GenerativeModel('gemini-2.5-flash')
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# --- Helper Functions ---
def get_weather(location: str):
    """Calls a real Weather API to get current weather info."""
    try:
        # Check if API key is available
        if not WEATHER_API_KEY:
            return f"Weather data for {location} is unavailable. API key not configured."
            
        response = requests.get(f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no")
        response.raise_for_status()
        data = response.json()
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']
        return f"The weather in {location} is {temp}°C with {condition}. Dress accordingly."
    except requests.exceptions.RequestException as e:
        print(f"Weather API request failed: {e}")
        return f"Weather data for {location} is unavailable. Assume mild conditions."
    except KeyError as e:
        print(f"Weather API response missing expected data: {e}")
        return f"Weather data for {location} is unavailable. Assume mild conditions."
    except Exception as e:
        print(f"Unexpected error getting weather: {e}")
        return f"Weather data for {location} is unavailable. Assume mild conditions."

def semantic_search(query_text: str, collection_name: str, user_id: str = None, n_results: int = 3):
    """Performs a semantic search on a specified ChromaDB collection."""
    try:
        if collection_name not in CHROMA_COLLECTIONS:
            print(f"Collection {collection_name} not found")
            return []
        
        collection = CHROMA_COLLECTIONS[collection_name]
        query_embedding = create_embedding(query_text)
        
        if not query_embedding:
            return []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'meta': results['metadatas'][0][i] if results['metadatas'][0] else {},
                'distance': results['distances'][0][i] if results.get('distances') else 0
            })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

# --- Core Logic ---
def generate_style_recommendation(user_id: str, user_prompt: str, location: str, emotion: str):
    """Orchestrates the entire Dual-RAG process."""
    
    # Get weather information
    weather_info = get_weather(location)
    
    # Search for celebrity style inspiration
    twin_prompt = f"Based on the user's request '{user_prompt}' and their emotion '{emotion}', find a celebrity style."
    twin_results = semantic_search(twin_prompt, COLLECTION_CELEB_STYLES, n_results=1)
    
    celebrity_twin = twin_results[0]['meta'].get('celebrity', 'Zendaya') if twin_results else "Zendaya"
    twin_description = twin_results[0]['text'] if twin_results else "A versatile and chic style icon."

    # Generate outfit concept
    concept_prompt = f"""
    You are StyleSense AI. Based on the user's prompt '{user_prompt}', the weather '{weather_info}', and inspiration from {celebrity_twin}, conceptualize one ideal outfit.
    Respond ONLY with a detailed list of 3 clothing items (e.g., 'A tailored navy blue blazer', 'White silk blouse', 'High-waisted black trousers').
    """
    
    try:
        concept_response = GENERATIVE_MODEL.generate_content(concept_prompt)
        outfit_concept_text = concept_response.text.strip()
        outfit_concept_list = [item.strip() for item in outfit_concept_text.split('\n') if item.strip()]
    except Exception as e:
        print(f"Error generating outfit concept: {e}")
        outfit_concept_list = ["Casual shirt", "Comfortable jeans", "Sneakers"]

    items_owned = []
    items_to_buy = []
    
    # Check user's wardrobe for each item
    for item_concept in outfit_concept_list[:3]:  # Limit to 3 items
        if not item_concept:
            continue
            
        wardrobe_results = semantic_search(item_concept, COLLECTION_ORDER_HISTORY, user_id=user_id, n_results=1)
        
        if wardrobe_results:
            items_owned.append({
                "item": item_concept,
                "owned_item": wardrobe_results[0]['text'],
                "confidence": round(1 - wardrobe_results[0].get('distance', 0.5), 2)
            })
        else:
            # Search for similar items to buy
            catalog_results = semantic_search(item_concept, COLLECTION_MYNTRA_CATALOG, n_results=1)
            
            if catalog_results:
                items_to_buy.append({
                    "item": item_concept,
                    "suggested_product": catalog_results[0]['text'],
                    "brand": catalog_results[0]['meta'].get('brand', 'Unknown'),
                    "link": catalog_results[0]['meta'].get('link', ''),
                    "confidence": round(1 - catalog_results[0].get('distance', 0.5), 2)
                })
            else:
                items_to_buy.append({
                    "item": item_concept,
                    "suggested_product": f"Search for: {item_concept}",
                    "brand": "Various",
                    "link": "",
                    "confidence": 0.7
                })

    # Generate final recommendation
    final_prompt = f"""
    Create a cohesive style recommendation summary:
    - User wants: {user_prompt}
    - Weather: {weather_info}
    - Celebrity inspiration: {celebrity_twin}
    - Items owned: {[item['owned_item'] for item in items_owned]}
    - Items to buy: {[item['suggested_product'] for item in items_to_buy]}
    
    Provide styling tips and how to put the look together.
    """
    
    try:
        final_response = GENERATIVE_MODEL.generate_content(final_prompt)
        final_recommendation = final_response.text.strip()
    except Exception as e:
        print(f"Error generating final recommendation: {e}")
        final_recommendation = f"Style inspiration from {celebrity_twin}. Mix your owned items with suggested purchases for a complete look."

    return {
        "celebrity_twin": celebrity_twin,
        "weather_info": weather_info,
        "final_recommendation": final_recommendation,
        "items_owned": items_owned,
        "items_to_buy": items_to_buy
    }