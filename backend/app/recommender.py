import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from database import CHROMA_COLLECTIONS, COLLECTION_PRODUCT_CATALOG, COLLECTION_USER_WARDROBE, COLLECTION_STYLE_INSPIRATION, EMBEDDING_MODEL

# --- Setup ---
load_dotenv()
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# --- Helper Functions ---

def get_weather(location: str):
    """Mocks or calls a real Weather API (e.g., OpenWeatherMap)."""
    try:
        # Example API call structure (requires an actual key and endpoint)
        # response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric")
        # data = response.json()
        
        # HACKATHON MOCK: Simulate a response
        temp = 28 
        condition = "Sunny with a chance of light breeze"
        return f"The weather in {location} is {temp}°C and {condition}. Dress light but consider a jacket."
    except Exception:
        return f"Weather data for {location} is unavailable. Assume mild conditions."

def semantic_search(query_text: str, collection_name: str, user_id: str = None, n_results: int = 3):
    """Performs a semantic search on a specified ChromaDB collection."""
    try:
        # 1. Embed the search query
        query_vector = EMBEDDING_MODEL.encode(query_text).tolist()
        
        # 2. Build the filter for user-specific data
        filter_clause = {"user_id": user_id} if user_id else None
        
        # 3. Query the collection
        results = CHROMA_COLLECTIONS[collection_name].query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=filter_clause,
            include=['documents', 'metadatas']
        )
        
        # Format results: [{'text': doc, 'meta': meta}, ...]
        formatted_results = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            formatted_results.append({'text': doc, 'meta': meta})
            
        return formatted_results

    except Exception as e:
        print(f"Search failed for {collection_name}: {e}")
        return []

# --- Core Logic ---

def generate_style_recommendation(user_id: str, user_prompt: str, location: str, emotion: str):
    """
    Orchestrates the entire Dual-RAG process.
    """
    
    # 1. Get Contextual Data
    weather_info = get_weather(location)
    
    # 2. Find "Fashion Twin" (Style Inspiration RAG)
    # The prompt finds a twin that matches the user's current style AND the desired vibe
    twin_prompt = f"The user's current style is defined by their closet. Based on their need: '{user_prompt}' and their current emotion: '{emotion}', find a celebrity who is the perfect style twin to match this vibe."
    
    # NOTE: For a real twin match, we would embed the user's entire wardrobe/profile first.
    # For the hackathon, we use the prompt to search the celebrity index.
    twin_results = semantic_search(twin_prompt, COLLECTION_STYLE_INSPIRATION, n_results=1)
    
    if not twin_results:
        celebrity_twin = "Zendaya (Default Style Twin)"
        twin_description = "A sophisticated, versatile style icon."
    else:
        celebrity_twin = twin_results[0]['meta'].get('celebrity', 'Unknown Twin')
        twin_description = twin_results[0]['text']

    # 3. LLM Generates Internal Outfit Concept
    # We ask the LLM to design the perfect outfit first
    concept_prompt = f"""
    You are StyleSense AI. The user is: '{user_id}'.
    User Prompt: '{user_prompt}'
    User Emotion: '{emotion}'
    Weather: {weather_info}
    Inspiration: {celebrity_twin} - {twin_description}

    First, conceptualize one high-level outfit inspired by {celebrity_twin} that fits the prompt, emotion, and weather.
    Respond ONLY with a detailed list of 3 clothing items (e.g., 'A tailored navy blue blazer', 'White silk blouse', 'High-waisted black trousers').
    """
    # Use a faster, constrained call to get the structured output
    concept_response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4-turbo",  # Use a powerful model for reasoning
        messages=[{"role": "user", "content": concept_prompt}],
        temperature=0.3
    )
    # This concept is the 'search query' for the RAG
    outfit_concept_list = concept_response.choices[0].message.content.split('\n')

    # 4. Dual RAG Retrieval
    items_owned = []
    items_to_buy = []
    
    for item_concept in outfit_concept_list:
        # Search User's Closet
        owned_results = semantic_search(item_concept, COLLECTION_USER_WARDROBE, user_id=user_id, n_results=1)
        if owned_results and owned_results[0]['text'] != item_concept: # Found a close match
            items_owned.append(owned_results[0]['text'])
        else:
            # If not owned, search the Product Catalog for a shoppable match
            buy_results = semantic_search(item_concept, COLLECTION_PRODUCT_CATALOG, n_results=1)
            if buy_results:
                # Mock a link for the hackathon
                link = f"http://myntra.com/product/{buy_results[0]['meta'].get('brand', 'N/A')}"
                items_to_buy.append({"name": buy_results[0]['text'], "link": link})

    # 5. Final LLM Synthesis
    final_synthesis_prompt = f"""
    You are StyleSense AI. Your goal is to deliver the final, highly personalized recommendation.
    User Prompt: '{user_prompt}'
    Weather: {weather_info}
    Inspiration: {celebrity_twin}

    Items the user should use from their closet: {items_owned if items_owned else 'None found.'}
    New items to buy to complete the look: {items_to_buy if items_to_buy else 'None needed.'}

    Craft a seamless, encouraging response. 
    1. Start by mentioning the twin and the confidence vibe.
    2. Suggest the full outfit, clearly telling the user which items to **Use** and which to **Buy**.
    3. Include a final, weather-aware styling tip.
    4. Respond with just the final text of the recommendation.
    """
    
    final_response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": final_synthesis_prompt}],
        temperature=0.7
    )

    return {
        "celebrity_twin": celebrity_twin,
        "weather_info": weather_info,
        "final_recommendation": final_response.choices[0].message.content,
        "items_owned": items_owned,
        "items_to_buy": [item['name'] for item in items_to_buy] # Return just names for Pydantic model
    }