# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# def test_gemini_api():
#     """Test Gemini API access and available models."""
    
#     # Check if API key exists
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         print("❌ No GEMINI_API_KEY found in .env file")
#         print("💡 Add GEMINI_API_KEY=your_key_here to your .env file")
#         return False
    
#     print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    
#     # Configure Gemini
#     genai.configure(api_key=api_key)
    
#     try:
#         print("\n🔍 Checking API connection...")
        
#         # List available models
#         models = list(genai.list_models())
#         print(f"✅ API connection successful!")
#         print(f"📋 Available models ({len(models)} total):")
        
#         vision_models = []
#         for model in models:
#             model_name = model.name.replace('models/', '')
#             print(f"   • {model_name}")
            
#             # Check if it's likely a vision model
#             if any(keyword in model_name.lower() for keyword in ['flash', '1.5', '2.5']) and 'pro' not in model_name:
#                 vision_models.append(model_name)
        
#         print(f"\n🖼️ Recommended vision models: {vision_models}")
        
#         # Test a simple text generation
#         print(f"\n🧪 Testing text generation...")
#         try:
#             test_models = ['gemini-1.5-flash', 'gemini-2.5-flash', 'gemini-1.5-pro']
            
#             for model_name in test_models:
#                 try:
#                     model = genai.GenerativeModel(model_name)
#                     response = model.generate_content("Say 'Hello from Gemini!'")
#                     if response.text:
#                         print(f"✅ {model_name}: {response.text.strip()}")
#                         print(f"🎉 RECOMMENDED MODEL FOR YOUR PROJECT: {model_name}")
#                         break
#                 except Exception as e:
#                     print(f"❌ {model_name}: {str(e)[:100]}...")
#                     continue
                    
#         except Exception as e:
#             print(f"❌ Text generation test failed: {e}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ API connection failed: {e}")
#         print("\n🔧 Troubleshooting:")
#         print("1. Check your API key at: https://aistudio.google.com/app/apikey")
#         print("2. Ensure your API key has proper permissions")
#         print("3. Check if there are regional restrictions")
#         return False

# def test_vision_capability():
#     """Test vision capabilities with a simple prompt."""
#     print("\n🖼️ Testing vision model capability...")
    
#     try:
#         # Try the recommended models
#         models_to_try = ['gemini-1.5-flash', 'gemini-2.5-flash', 'gemini-1.5-pro']
        
#         for model_name in models_to_try:
#             try:
#                 model = genai.GenerativeModel(model_name)
                
#                 # Test if model accepts multimodal input (without actually sending an image)
#                 response = model.generate_content("If I were to send you an image of fashion clothing, how would you describe it?")
                
#                 if response.text:
#                     print(f"✅ {model_name} supports vision tasks!")
#                     print(f"📝 Sample response: {response.text[:100]}...")
#                     return model_name
                    
#             except Exception as e:
#                 print(f"❌ {model_name} vision test failed: {str(e)[:100]}...")
#                 continue
                
#         print("❌ No working vision models found")
#         return None
        
#     except Exception as e:
#         print(f"❌ Vision capability test failed: {e}")
#         return None

# if __name__ == "__main__":
#     print("🔍 Gemini API Diagnostic Tool")
#     print("=" * 50)
    
#     if test_gemini_api():
#         working_model = test_vision_capability()
        
#         if working_model:
#             print(f"\n🎯 SOLUTION FOR YOUR DATA LOADER:")
#             print(f"Replace 'gemini-pro-vision' with '{working_model}' in your code")
#             print(f"Set SKIP_CELEBRITY_IMAGES = False")
#         else:
#             print(f"\n⚠️ RECOMMENDATION:")
#             print(f"Keep SKIP_CELEBRITY_IMAGES = True for now")
#             print(f"Your product catalog and order history should work fine")
#     else:
#         print(f"\n❌ Fix your API key first!")
#         print(f"Get it from: https://aistudio.google.com/app/apikey")