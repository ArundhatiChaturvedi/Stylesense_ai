import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from .database import CHROMA_COLLECTIONS, COLLECTION_MYNTRA_CATALOG, COLLECTION_USER_STYLES, COLLECTION_CELEB_STYLES, create_embedding
from sentence_transformers import SentenceTransformer

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
GENERATIVE_MODEL = genai.GenerativeModel('gemini-2.5-flash')
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

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
            valid_emotions = ['confident', 'casual', 'romantic', 'professional', 'adventurous', 
                            'cozy', 'elegant', 'playful', 'edgy', 'minimalist', 'bohemian', 'sporty']
            if emotion in valid_emotions:
                return emotion
        
        return "confident"
        
    except Exception as e:
        print(f"Error extracting emotion: {e}")
        return "confident"

def get_weather(location: str):
    """Calls a real Weather API to get current weather info."""
    try:
        if not WEATHER_API_KEY:
            return f"Weather data for {location} is unavailable. Assume mild conditions."
            
        response = requests.get(
            f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']
        return f"The weather in {location} is {temp}°C with {condition}. Dress accordingly."
    except Exception as e:
        print(f"Weather API error: {e}")
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
            print("Failed to create embedding for query")
            return []
        
        where_clause = None
        if collection_name == COLLECTION_USER_STYLES and user_id:
            where_clause = {"user_id": user_id}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'meta': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results.get('distances') and results['distances'][0] else 0.5
                })
        
        print(f"Semantic search found {len(formatted_results)} results for '{query_text}' in {collection_name}")
        return formatted_results
        
    except Exception as e:
        print(f"Error in semantic search for '{query_text}' in {collection_name}: {e}")
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
    
    Keep descriptions detailed but concise. Focus on specific clothing items, not accessories.
    """
    
    try:
        response = GENERATIVE_MODEL.generate_content(concept_prompt)
        if response.text:
            outfit_text = response.text.strip()
            print(f"Generated outfit concept: {outfit_text}")
            
            lines = [line.strip() for line in outfit_text.split('\n') if line.strip()]
            outfit_items = []
            
            for line in lines:
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    if '. ' in line:
                        clean_item = line.split('. ', 1)[1].strip()
                    elif ') ' in line:
                        clean_item = line.split(') ', 1)[1].strip()
                    elif line.startswith('- '):
                        clean_item = line[2:].strip()
                    elif line.startswith('• '):
                        clean_item = line[2:].strip()
                    else:
                        clean_item = line[1:].strip() if len(line) > 1 else line
                    
                    if clean_item:
                        outfit_items.append(clean_item)
            
            if outfit_items:
                print(f"Parsed outfit items: {outfit_items}")
                return outfit_items[:3]
        
    except Exception as e:
        print(f"Error generating outfit concept: {e}")
        
    fallback_outfits = {
        "professional": ["Tailored blazer", "Crisp button-down shirt", "Dress pants"],
        "casual": ["Comfortable jeans", "Soft cotton t-shirt", "Lightweight cardigan"],
        "elegant": ["Little black dress", "Statement jewelry", "Elegant heels"],
        "romantic": ["Flowy midi dress", "Soft cardigan", "Delicate accessories"],
        "confident": ["Bold colored top", "Well-fitted jeans", "Statement jacket"]
    }
    
    return fallback_outfits.get(emotion, ["Casual shirt", "Comfortable jeans", "Versatile jacket"])

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
    Maximum 3-4 paragraphs.
    """
    
    try:
        response = GENERATIVE_MODEL.generate_content(final_prompt)
        if response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Error generating final recommendation: {e}")
    
    owned_items_text = ", ".join([item.get('owned_item', '') for item in items_owned]) if items_owned else "your existing wardrobe pieces"
    buy_items_text = ", ".join([item.get('suggested_product', '') for item in items_to_buy]) if items_to_buy else "some versatile pieces"
    
    return f"Channel {celebrity_twin}'s effortless {emotion} style! Start with {owned_items_text} from your wardrobe. To complete the look, consider adding {buy_items_text}. The weather calls for {weather_info.lower()}, so layer smartly and choose breathable fabrics. Remember, confidence is your best accessory - own your style and make it uniquely yours!"

def generate_style_recommendation(user_id: str, user_prompt: str, location: str):
    """Orchestrates the entire Dual-RAG process with emotion extraction."""
    
    try:
        print(f"Starting style recommendation for user {user_id}")
        print(f"User prompt: {user_prompt}")
        print(f"Location: {location}")
        
        extracted_emotion = extract_emotion_from_prompt(user_prompt)
        print(f"Extracted emotion: {extracted_emotion}")
        
        weather_info = get_weather(location)
        print(f"Weather info: {weather_info}")
        
        twin_prompt = f"Based on the user's request '{user_prompt}' and their {extracted_emotion} mood, find a celebrity style that matches."
        twin_results = semantic_search(twin_prompt, COLLECTION_CELEB_STYLES, n_results=1)
        
        celebrity_twin = "Zendaya"
        celebrity_image_url = None
        
        if twin_results:
            celebrity_name = twin_results[0]['meta'].get('celebrity', 'Zendaya')
            celebrity_twin = celebrity_name.split('_')[0] if '_' in celebrity_name else celebrity_name
            celebrity_twin = celebrity_twin.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
            celebrity_twin = ' '.join(word.capitalize() for word in celebrity_twin.split())
            
            celebrity_image_url = twin_results[0]['meta'].get('image_url', '')
        
        print(f"Celebrity style inspiration: {celebrity_twin}")
        
        outfit_concept_list = generate_outfit_concept(user_prompt, weather_info, celebrity_twin, extracted_emotion)
        print(f"Generated outfit concept: {outfit_concept_list}")
        
        items_owned = []
        items_to_buy = []
        
        for item_concept in outfit_concept_list:
            if not item_concept or len(item_concept.strip()) < 3:
                continue
                
            print(f"Searching for: {item_concept}")
            
            style_results = semantic_search(item_concept, COLLECTION_USER_STYLES, user_id=user_id, n_results=3)
            
            best_match = None
            for result in style_results:
                if result['distance'] < 0.7:
                    best_match = result
                    break
            
            if best_match:
                items_owned.append({
                    "item": item_concept,
                    "owned_item": best_match['text'],
                    "confidence": round(max(0, 1 - best_match.get('distance', 0.5)), 2),
                    "source": best_match['meta'].get('source', 'user_style')
                })
                print(f"Found owned item: {best_match['text']} (confidence: {1 - best_match.get('distance', 0.5):.2f})")
            else:
                catalog_results = semantic_search(item_concept, COLLECTION_MYNTRA_CATALOG, n_results=3)
                
                if catalog_results:
                    best_product = catalog_results[0]
                    items_to_buy.append({
                        "item": item_concept,
                        "suggested_product": best_product['text'],
                        "brand": best_product['meta'].get('brand', 'Unknown'),
                        "link": best_product['meta'].get('link', ''),
                        "confidence": round(max(0, 1 - best_product.get('distance', 0.5)), 2)
                    })
                    print(f"Suggested to buy: {best_product['text']} (confidence: {1 - best_product.get('distance', 0.5):.2f})")
                else:
                    items_to_buy.append({
                        "item": item_concept,
                        "suggested_product": f"Look for: {item_concept}",
                        "brand": "Various brands",
                        "link": "",
                        "confidence": 0.7
                    })
                    print(f"No specific products found, added generic suggestion: {item_concept}")

        final_recommendation = generate_final_recommendation(
            user_prompt, weather_info, celebrity_twin, 
            items_owned, items_to_buy, extracted_emotion
        )

        result = {
            "celebrity_twin": celebrity_twin,
            "celebrity_image_url": celebrity_image_url,
            "weather_info": weather_info,
            "final_recommendation": final_recommendation,
            "items_owned": items_owned,
            "items_to_buy": items_to_buy,
            "extracted_emotion": extracted_emotion
        }
        
        print(f"Generated recommendation with {len(items_owned)} owned items and {len(items_to_buy)} items to buy")
        return result
        
    except Exception as e:
        print(f"Error in generate_style_recommendation: {e}")
        return {
            "celebrity_twin": "Zendaya",
            "celebrity_image_url": None,
            "weather_info": f"Weather information unavailable for {location}. Dress comfortably for the season.",
            "final_recommendation": f"Here's a personalized style suggestion based on your request: '{user_prompt}'. Consider mixing classic pieces with trendy accents to create a versatile look that reflects your personal style. Layer appropriately for the weather and choose pieces that make you feel confident and comfortable.",
            "items_owned": [],
            "items_to_buy": [
                {
                    "item": "versatile top",
                    "suggested_product": "Classic white button-down shirt",
                    "brand": "Various brands",
                    "link": "",
                    "confidence": 0.8
                }
            ],
            "extracted_emotion": "confident"
        }