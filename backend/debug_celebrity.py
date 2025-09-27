import os
import glob
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import time
from PIL import Image

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Your paths
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CELEBRITY_IMAGE_DIR = os.path.join(BASE_DATA_DIR, 'Celeb_FBI_Dataset')

def image_to_base64(image_path):
    """Convert image to base64 with better error handling."""
    try:
        # Check if file exists and is readable
        if not os.path.exists(image_path):
            return None, f"File not found: {image_path}"
        
        # Check file size (skip very large files)
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return None, f"File too large: {file_size} bytes"
        
        # Try to open with PIL first to validate image
        try:
            with Image.open(image_path) as img:
                img.verify()  # Verify it's a valid image
        except Exception as pil_error:
            return None, f"Invalid image file: {pil_error}"
        
        # Convert to base64
        with open(image_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_data, "Success"
            
    except Exception as e:
        return None, f"Encoding error: {e}"

def test_gemini_vision(base64_image, image_path):
    """Test Gemini vision with detailed error reporting."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": base64_image
        }
        
        prompt = "Describe this fashion style and outfit in detail, focusing on colors, patterns, style, and clothing items."
        
        response = model.generate_content([prompt, image_part])
        
        if response.text and len(response.text.strip()) > 10:
            return response.text.strip(), "Success"
        else:
            return None, f"Empty or too short response: '{response.text}'"
            
    except Exception as e:
        return None, f"Gemini API error: {e}"

def analyze_celebrity_dataset():
    """Analyze the celebrity dataset to understand the low success rate."""
    
    print("🔍 Analyzing Celebrity Dataset...")
    
    if not os.path.isdir(CELEBRITY_IMAGE_DIR):
        print(f"❌ Directory not found: {CELEBRITY_IMAGE_DIR}")
        return
    
    # Find all image files
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_paths.extend(glob.glob(os.path.join(CELEBRITY_IMAGE_DIR, ext)))
    
    print(f"📊 Found {len(image_paths)} image files")
    
    if len(image_paths) == 0:
        print("❌ No image files found!")
        return
    
    # Test first 20 images to identify issues
    print(f"\n🧪 Testing first 20 images...")
    
    stats = {
        'total_tested': 0,
        'encoding_success': 0,
        'encoding_failures': 0,
        'api_success': 0,
        'api_failures': 0,
        'encoding_errors': [],
        'api_errors': []
    }
    
    test_sample = image_paths[:20]  # Test first 20
    
    for i, image_path in enumerate(test_sample):
        print(f"\n📸 Testing {i+1}/20: {os.path.basename(image_path)}")
        stats['total_tested'] += 1
        
        # Test image encoding
        base64_data, encoding_result = image_to_base64(image_path)
        
        if base64_data:
            stats['encoding_success'] += 1
            print(f"  ✅ Encoding: Success ({len(base64_data)} chars)")
            
            # Test Gemini API
            time.sleep(1)  # Rate limiting
            description, api_result = test_gemini_vision(base64_data, image_path)
            
            if description:
                stats['api_success'] += 1
                print(f"  ✅ Gemini API: Success")
                print(f"  📝 Description: {description[:100]}...")
            else:
                stats['api_failures'] += 1
                stats['api_errors'].append(api_result)
                print(f"  ❌ Gemini API: {api_result}")
                
        else:
            stats['encoding_failures'] += 1
            stats['encoding_errors'].append(encoding_result)
            print(f"  ❌ Encoding: {encoding_result}")
    
    # Print summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"{'='*50}")
    print(f"Total tested: {stats['total_tested']}")
    print(f"Encoding success: {stats['encoding_success']}/{stats['total_tested']} ({stats['encoding_success']/stats['total_tested']*100:.1f}%)")
    print(f"API success: {stats['api_success']}/{stats['encoding_success']} ({stats['api_success']/max(1,stats['encoding_success'])*100:.1f}%)")
    
    if stats['encoding_errors']:
        print(f"\n❌ ENCODING ERRORS:")
        for error in set(stats['encoding_errors'][:5]):  # Show unique errors
            print(f"  • {error}")
    
    if stats['api_errors']:
        print(f"\n❌ API ERRORS:")
        for error in set(stats['api_errors'][:5]):  # Show unique errors
            print(f"  • {error}")
    
    # Calculate expected success rate
    if stats['encoding_success'] > 0 and stats['api_success'] > 0:
        expected_total_success = int(len(image_paths) * (stats['api_success'] / stats['encoding_success']) * (stats['encoding_success'] / stats['total_tested']))
        print(f"\n🎯 PROJECTED RESULTS:")
        print(f"Expected successful celebrity items: ~{expected_total_success}")
        print(f"You got: 8 items")
        
        if expected_total_success > 100:
            print(f"💡 RECOMMENDATION: Your dataset should work much better!")
            print(f"   The low count (8) suggests the process was interrupted or hit severe rate limits")
        else:
            print(f"💡 RECOMMENDATION: Dataset has quality issues")
    
    return stats

def check_rate_limits():
    """Test current rate limit status."""
    print(f"\n🚦 Testing Rate Limits...")
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        for i in range(5):
            start_time = time.time()
            response = model.generate_content(f"Say 'Test {i+1}'")
            end_time = time.time()
            
            if response.text:
                print(f"✅ Request {i+1}: Success ({end_time-start_time:.2f}s)")
            else:
                print(f"❌ Request {i+1}: Failed")
            
            time.sleep(0.1)  # Your current rate limit delay
            
    except Exception as e:
        print(f"❌ Rate limit test failed: {e}")

if __name__ == "__main__":
    print("🔍 Celebrity Dataset Diagnostic Tool")
    print("=" * 60)
    
    analyze_celebrity_dataset()
    check_rate_limits()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. If encoding success is low: Check image file quality")
    print(f"2. If API success is low: Increase rate limiting delay")  
    print(f"3. If both are high but you only got 8 items: Process was interrupted")