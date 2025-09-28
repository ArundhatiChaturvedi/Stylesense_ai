import os
import requests
import google.generativeai as genai
import google.generativeai as genai
from dotenv import load_dotenv
from .database import CHROMA_COLLECTIONS, COLLECTION_MYNTRA_CATALOG, COLLECTION_USER_STYLES, COLLECTION_CELEB_STYLES, create_embedding
from sentence_transformers import SentenceTransformer

# --- Setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
GENERATIVE_MODEL = genai.GenerativeModel('gemini-2.5-flash')  # Updated model name
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# --- Helper Functions ---
def extract_emotion_from_prompt(user_prompt: str):
    """Extract emotion/mood from user prompt using LLM."""
    try:
        emotion_prompt = f"""
        Analyze this user request and extract their emotional state or mood in ONE WORD:
        "{user_prompt}"
        
        Choose from: confident, casual, romantic, professional, adventurous, cozy, elegant, playful, edgy, minimalist, bohemian, sporty
        Respond with only the emotion word, nothing else.
        """
        
        response = GENERATIVE_MODEL.generate_content(emotion_prompt)
        if response.text:
            emotion = response.text.strip().lower()
            # Validate against our expected emotions
            valid_emotions = ['confident', 'casual', 'romantic', 'professional', 'adventurous', 
                            'cozy', 'elegant', 'playful', 'edgy', 'minimalist', 'bohemian', 'sporty']
            if emotion in valid_emotions:
                return emotion
        
        return "confident"  # Default fallback
        
    except Exception as e:
        print(f"Error extracting emotion: {e}")
        return "confident"

def get_weather(location: str):
    """Calls a real Weather API to get current weather info."""
    """Calls a real Weather API to get current weather info."""
    try:
        if not WEATHER_API_KEY:
            return f"Weather data for {location} is unavailable. API key not configured. Assume mild conditions."
            
        response = requests.get(
            f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no",
            timeout=5
        )
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
        
        # For user styles, filter by user_id
        where_clause = None
        if collection_name == COLLECTION_USER_STYLES and user_id:
            where_clause = {"user_id": user_id}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'meta': results['metadatas'][0][i] if results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else 0
                })
        
        return formatted_results
        
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        print(f"Error in semantic search: {e}")
        return []

def generate_outfit_concept(user_prompt: str, weather_info: str, celebrity_twin: str, emotion: str):
    """Generate outfit concept using LLM."""
    concept_prompt = f"""
    You are StyleSense AI. Create an outfit concept based on:
    
    User Request: "{user_prompt}"
    User's Mood: {emotion}
    Weather: {weather_info}
    Style Inspiration: {celebrity_twin}
    
    Respond with EXACTLY 3 clothing items in this format:
    1. [clothing item description]
    2. [clothing item description]  
    3. [clothing item description]
    
    Example:
    1. A tailored navy blue blazer
    2. White silk blouse with subtle texture
    3. High-waisted black trousers
    
    Keep descriptions detailed but concise.
    """
    
    try:
        response = GENERATIVE_MODEL.generate_content(concept_prompt)
        if response.text:
            outfit_text = response.text.strip()
            # Parse the numbered list
            lines = [line.strip() for line in outfit_text.split('\n') if line.strip()]
            outfit_items = []
            
            for line in lines:
                # Remove numbering (1., 2., etc.)
                if line and (line[0].isdigit() or line.startswith('-')):
                    clean_item = line[2:].strip() if len(line) > 2 else line
                    outfit_items.append(clean_item)
            
            return outfit_items[:3] if outfit_items else ["Casual shirt", "Comfortable jeans", "Sneakers"]
        
    except Exception as e:
        print(f"Error generating outfit concept: {e}")
        
    return ["Casual shirt", "Comfortable jeans", "Sneakers"]

def generate_final_recommendation(user_prompt: str, weather_info: str, celebrity_twin: str, 
                                items_owned: list, items_to_buy: list, emotion: str):
    """Generate final styled recommendation."""
    final_prompt = f"""
    Create a personalized style recommendation for the user:
    
    User Request: "{user_prompt}"
    User's Mood: {emotion}
    Weather Context: {weather_info}
    Celebrity Style Inspiration: {celebrity_twin}
    
    Items they already own: {[item.get('owned_item', '') for item in items_owned]}
    Items they should consider buying: {[item.get('suggested_product', '') for item in items_to_buy]}
    
    Create a cohesive, inspiring recommendation that includes:
    1. A style summary inspired by the celebrity
    2. How to style their existing pieces
    3. Why the suggested purchases complete the look
    4. Weather-appropriate styling tips
    5. Confidence-boosting styling advice
    
    Keep it personal, practical, and inspiring. Write in a friendly, expert stylist tone.
    """
    
    try:
        response = GENERATIVE_MODEL.generate_content(final_prompt)
        if response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Error generating final recommendation: {e}")
    
    return f"Channel {celebrity_twin}'s effortless {emotion} style! Mix your existing pieces with these suggested items for a perfect look that matches the weather and your personal aesthetic."

# --- Core Logic ---
def generate_style_recommendation(user_id: str, user_prompt: str, location: str):
    """Orchestrates the entire Dual-RAG process with emotion extraction."""
    
    # Extract emotion from user prompt
    extracted_emotion = extract_emotion_from_prompt(user_prompt)
    print(f"Extracted emotion: {extracted_emotion}")
    
    # Get weather information
    weather_info = get_weather(location)
    
    # Search for celebrity style inspiration
    twin_prompt = f"Based on the user's request '{user_prompt}' and their {extracted_emotion} mood, find a celebrity style that matches."
    twin_results = semantic_search(twin_prompt, COLLECTION_CELEB_STYLES, n_results=1)
    
    celebrity_twin = "Zendaya"  # Default fallback
    if twin_results:
        celebrity_twin = twin_results[0]['meta'].get('celebrity', 'Zendaya')
        # Clean up celebrity name (remove file extensions, numbers)
        celebrity_twin = celebrity_twin.split('_')[0] if '_' in celebrity_twin else celebrity_twin
        celebrity_twin = celebrity_twin.replace('.jpg', '').replace('.png', '')
    
    # Generate outfit concept
    outfit_concept_list = generate_outfit_concept(user_prompt, weather_info, celebrity_twin, extracted_emotion)
    
    items_owned = []
    items_to_buy = []
    
    # Check user's style collection for each outfit item
    for item_concept in outfit_concept_list:
        if not item_concept:
            continue
            
        # Search in user's styles (both wardrobe and purchase history)
        style_results = semantic_search(item_concept, COLLECTION_USER_STYLES, user_id=user_id, n_results=2)
        
        # Find best match from user's items
        best_match = None
        for result in style_results:
            if result['distance'] < 0.7:  # Good match threshold
                best_match = result
                break
        
        if best_match:
            items_owned.append({
                "item": item_concept,
                "owned_item": best_match['text'],
                "confidence": round(1 - best_match.get('distance', 0.5), 2),
                "source": best_match['meta'].get('source', 'user_style')
            })
        else:
            # Search for items to buy
            catalog_results = semantic_search(item_concept, COLLECTION_MYNTRA_CATALOG, n_results=2)
            
            if catalog_results:
                best_product = catalog_results[0]
                items_to_buy.append({
                    "item": item_concept,
                    "suggested_product": best_product['text'],
                    "brand": best_product['meta'].get('brand', 'Unknown'),
                    "link": best_product['meta'].get('link', ''),
                    "confidence": round(1 - best_product.get('distance', 0.5), 2)
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
    final_recommendation = generate_final_recommendation(
        user_prompt, weather_info, celebrity_twin, 
        items_owned, items_to_buy, extracted_emotion
    )

    return {
        "celebrity_twin": celebrity_twin,
        "weather_info": weather_info,
        "final_recommendation": final_recommendation,
        "final_recommendation": final_recommendation,
        "items_owned": items_owned,
        "items_to_buy": items_to_buy,
        "extracted_emotion": extracted_emotion
    }