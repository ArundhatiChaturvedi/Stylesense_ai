"""
Comprehensive test script for StyleSense AI Backend
Tests all functionality including wardrobe upload, recommendations, and all endpoints
"""

import requests
import json
import base64
from pathlib import Path
import time
import io
from PIL import Image, ImageDraw
import os

API_BASE_URL = "http://localhost:8080"

class StyleSenseTestSuite:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'details': []
        }
    
    def log_test(self, test_name, passed, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"     {message}")
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"     {key}: {value}")
        
        self.test_results['passed' if passed else 'failed'] += 1
        self.test_results['details'].append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details
        })
        print()
    
    def create_test_image(self, text="Test Clothing Item", size=(400, 400)):
        """Create a simple test image for wardrobe upload"""
        img = Image.new('RGB', size, color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add some text to make it look like clothing
        draw.text((50, 50), text, fill='black')
        draw.rectangle([100, 100, 300, 350], outline='darkblue', width=3)
        draw.text((130, 200), "Fashion Item", fill='darkblue')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def test_api_health(self):
        """Test basic API health"""
        try:
            response = requests.get(f"{self.base_url}/")
            root_data = response.json()
            
            health_response = requests.get(f"{self.base_url}/health")
            health_data = health_response.json()
            
            passed = (response.status_code == 200 and 
                     health_response.status_code == 200 and
                     health_data.get('status') == 'healthy')
            
            self.log_test(
                "API Health Check",
                passed,
                f"API Version: {root_data.get('version', 'unknown')}",
                health_data
            )
            return passed
            
        except Exception as e:
            self.log_test("API Health Check", False, f"API not reachable: {e}")
            return False
    
    def test_collections_status(self):
        """Test collections status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/collections/status")
            data = response.json()
            
            collections = data.get('collections', {})
            passed = (response.status_code == 200 and 
                     len(collections) > 0 and
                     data.get('status') == 'healthy')
            
            self.log_test(
                "Collections Status",
                passed,
                f"Collections loaded: {len(collections)}",
                collections
            )
            return data if passed else None
            
        except Exception as e:
            self.log_test("Collections Status", False, f"Error: {e}")
            return None
    
    def test_user_status(self, user_id):
        """Test user status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/user/{user_id}/status")
            data = response.json()
            
            passed = response.status_code == 200
            
            self.log_test(
                f"User Status Check ({user_id})",
                passed,
                f"User exists: {data.get('user_exists', False)}",
                {
                    'Total items': data.get('total_items', 0),
                    'Wardrobe items': data.get('wardrobe_items_count', 0),
                    'Purchase history': data.get('purchase_history_count', 0)
                }
            )
            return data if passed else None
            
        except Exception as e:
            self.log_test(f"User Status Check ({user_id})", False, f"Error: {e}")
            return None
    
    def test_wardrobe_upload_base64(self, user_id, num_images=3):
        """Test wardrobe upload using base64 images"""
        try:
            uploaded_count = 0
            
            for i in range(num_images):
                test_image_b64 = self.create_test_image(f"Test Item {i+1}")
                
                payload = {
                    "user_id": user_id,
                    "image_base64": test_image_b64
                }
                
                response = requests.post(f"{self.base_url}/user/styles/upload-base64", json=payload)
                
                if response.status_code == 200:
                    uploaded_count += 1
                    time.sleep(1)  # Rate limiting
            
            passed = uploaded_count > 0
            self.log_test(
                "Wardrobe Upload (Base64)",
                passed,
                f"Successfully uploaded {uploaded_count}/{num_images} images",
                {"uploaded_count": uploaded_count}
            )
            return uploaded_count
            
        except Exception as e:
            self.log_test("Wardrobe Upload (Base64)", False, f"Error: {e}")
            return 0
    
    def test_load_order_history(self, user_id):
        """Test loading order history"""
        try:
            data = {"user_id": user_id}
            response = requests.post(f"{self.base_url}/user/styles/load-orders", data=data)
            result = response.json()
            
            passed = response.status_code == 200 and result.get('success', False)
            
            self.log_test(
                "Load Order History",
                passed,
                f"Items loaded: {result.get('items_loaded', 0)}",
                result
            )
            return result if passed else None
            
        except Exception as e:
            self.log_test("Load Order History", False, f"Error: {e}")
            return None
    
    def test_search_functionality(self, user_id):
        """Test all search endpoints"""
        search_queries = [
            "blue shirt",
            "casual jeans",
            "formal dress",
            "sneakers",
            "elegant outfit"
        ]
        
        # Test user styles search
        user_search_passed = 0
        for query in search_queries[:2]:  # Test fewer queries
            try:
                payload = {
                    "query": query,
                    "user_id": user_id,
                    "max_results": 5
                }
                response = requests.post(f"{self.base_url}/user/styles/search", json=payload)
                if response.status_code == 200:
                    user_search_passed += 1
            except Exception as e:
                print(f"User search error for '{query}': {e}")
        
        self.log_test(
            "User Styles Search",
            user_search_passed > 0,
            f"Successful searches: {user_search_passed}/2"
        )
        
        # Test product search
        product_search_passed = 0
        for query in search_queries[:2]:
            try:
                payload = {
                    "query": query,
                    "max_results": 5
                }
                response = requests.post(f"{self.base_url}/products/search", json=payload)
                if response.status_code == 200:
                    product_search_passed += 1
            except Exception as e:
                print(f"Product search error for '{query}': {e}")
        
        self.log_test(
            "Product Catalog Search",
            product_search_passed > 0,
            f"Successful searches: {product_search_passed}/2"
        )
        
        # Test celebrity styles search
        celebrity_search_passed = 0
        for query in ["elegant style", "casual chic"]:
            try:
                payload = {
                    "query": query,
                    "max_results": 5
                }
                response = requests.post(f"{self.base_url}/celebrity-styles/search", json=payload)
                if response.status_code == 200:
                    celebrity_search_passed += 1
            except Exception as e:
                print(f"Celebrity search error for '{query}': {e}")
        
        self.log_test(
            "Celebrity Styles Search",
            celebrity_search_passed > 0,
            f"Successful searches: {celebrity_search_passed}/2"
        )
    
    def test_outfit_recommendations(self, user_id):
        """Test outfit recommendation endpoint"""
        try:
            payload = {
                "query": "business casual outfit",
                "user_id": user_id,
                "max_results": 10
            }
            
            response = requests.post(f"{self.base_url}/recommend/outfit", json=payload)
            data = response.json()
            
            passed = (response.status_code == 200 and 
                     'recommendations' in data)
            
            self.log_test(
                "Outfit Recommendations",
                passed,
                f"Recommendations generated for query: '{payload['query']}'",
                {
                    'User styles found': len(data.get('recommendations', {}).get('matching_user_styles', [])),
                    'Products suggested': len(data.get('recommendations', {}).get('suggested_products', [])),
                    'Style inspiration': len(data.get('recommendations', {}).get('style_inspiration', []))
                }
            )
            return data if passed else None
            
        except Exception as e:
            self.log_test("Outfit Recommendations", False, f"Error: {e}")
            return None
    
    def test_ai_style_recommendations(self, user_id):
        """Test AI-powered style recommendations with emotion extraction"""
        test_prompts = [
            {
                "prompt": "I need a confident outfit for a job interview",
                "expected_emotion": "professional"
            },
            {
                "prompt": "Something casual and cozy for a coffee date",
                "expected_emotion": "casual"
            },
            {
                "prompt": "I want to look elegant for a dinner party",
                "expected_emotion": "elegant"
            }
        ]
        
        successful_recommendations = 0
        
        for test_case in test_prompts:
            try:
                payload = {
                    "user_id": user_id,
                    "user_prompt": test_case["prompt"],
                    "current_location": "Mumbai"
                }
                
                print(f"Testing AI recommendation: '{test_case['prompt']}'")
                response = requests.post(f"{self.base_url}/recommend", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    successful_recommendations += 1
                    
                    print(f"     Celebrity Twin: {data.get('celebrity_twin')}")
                    print(f"     Extracted Emotion: {data.get('extracted_emotion')}")
                    print(f"     Items Owned: {len(data.get('items_owned', []))}")
                    print(f"     Items to Buy: {len(data.get('items_to_buy', []))}")
                    print()
                    
                elif response.status_code == 400:
                    error_data = response.json()
                    if "must upload wardrobe" in error_data.get('detail', ''):
                        print(f"     User needs wardrobe data (expected)")
                    else:
                        print(f"     Error: {error_data.get('detail')}")
                else:
                    print(f"     HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"     Error: {e}")
            
            time.sleep(2)  # Rate limiting for AI calls
        
        passed = successful_recommendations > 0
        self.log_test(
            "AI Style Recommendations",
            passed,
            f"Successful recommendations: {successful_recommendations}/{len(test_prompts)}",
            {"ai_features": "emotion_extraction, weather_integration, celebrity_matching"}
        )
        
        return successful_recommendations
    
    def test_user_management(self, user_id):
        """Test user management endpoints"""
        try:
            # Test user stats
            stats_response = requests.get(f"{self.base_url}/user/{user_id}/styles/stats")
            stats_passed = stats_response.status_code == 200
            
            if stats_passed:
                stats_data = stats_response.json()
                self.log_test(
                    "User Style Stats",
                    True,
                    f"Total items: {stats_data.get('total_style_items', 0)}",
                    stats_data
                )
            else:
                self.log_test("User Style Stats", False, f"HTTP {stats_response.status_code}")
            
            return stats_passed
            
        except Exception as e:
            self.log_test("User Management", False, f"Error: {e}")
            return False
    
    def test_data_cleanup(self, user_id):
        """Test clearing user data (optional)"""
        try:
            # Clear only wardrobe uploads, keep purchase history
            response = requests.delete(f"{self.base_url}/user/{user_id}/wardrobe?source_type=wardrobe_upload")
            data = response.json()
            
            passed = response.status_code == 200
            
            self.log_test(
                "Data Cleanup (Wardrobe)",
                passed,
                f"Remaining items: {data.get('remaining_items', 'unknown')}",
                data
            )
            return passed
            
        except Exception as e:
            self.log_test("Data Cleanup", False, f"Error: {e}")
            return False
    
    def run_comprehensive_test(self, test_user_id="test_user_comprehensive"):
        """Run all tests in sequence"""
        print("=" * 80)
        print("StyleSense AI - COMPREHENSIVE SYSTEM TEST")
        print("=" * 80)
        print(f"Testing with user ID: {test_user_id}")
        print(f"API Base URL: {self.base_url}")
        print("=" * 80)
        print()
        
        # Phase 1: Basic System Health
        print("🔍 PHASE 1: System Health Checks")
        print("-" * 40)
        
        if not self.test_api_health():
            print("❌ Critical: API not accessible. Stopping tests.")
            return self.get_summary()
        
        collections_data = self.test_collections_status()
        if not collections_data:
            print("❌ Critical: Collections not accessible. Stopping tests.")
            return self.get_summary()
        
        # Phase 2: User Setup
        print("👤 PHASE 2: User Management")
        print("-" * 40)
        
        # Check initial user status
        initial_status = self.test_user_status(test_user_id)
        
        # Upload test wardrobe images
        uploaded_images = self.test_wardrobe_upload_base64(test_user_id, 2)
        
        # Load order history if not already loaded
        self.test_load_order_history(test_user_id)
        
        # Check user status after data loading
        final_user_status = self.test_user_status(test_user_id)
        
        # Phase 3: Search Functionality
        print("🔎 PHASE 3: Search Capabilities")
        print("-" * 40)
        
        self.test_search_functionality(test_user_id)
        
        # Phase 4: Recommendation Systems
        print("🤖 PHASE 4: AI Recommendation Systems")
        print("-" * 40)
        
        self.test_outfit_recommendations(test_user_id)
        
        # Only test AI recommendations if user has data
        if final_user_status and final_user_status.get('user_exists'):
            self.test_ai_style_recommendations(test_user_id)
        else:
            self.log_test(
                "AI Style Recommendations", 
                False, 
                "Skipped - User has no style data"
            )
        
        # Phase 5: User Management Features
        print("⚙️ PHASE 5: User Management")
        print("-" * 40)
        
        self.test_user_management(test_user_id)
        
        # Phase 6: Cleanup (Optional)
        print("🧹 PHASE 6: Data Management")
        print("-" * 40)
        
        # Uncomment if you want to test cleanup
        # self.test_data_cleanup(test_user_id)
        
        print("=" * 80)
        return self.get_summary()
    
    def get_summary(self):
        """Get test results summary"""
        total_tests = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            'total_tests': total_tests,
            'passed': self.test_results['passed'],
            'failed': self.test_results['failed'],
            'pass_rate': round(pass_rate, 1),
            'details': self.test_results['details']
        }
        
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌") 
        print(f"Pass Rate: {pass_rate:.1f}%")
        print()
        
        if self.test_results['failed'] > 0:
            print("❌ Failed Tests:")
            for detail in self.test_results['details']:
                if not detail['passed']:
                    print(f"   • {detail['test']}: {detail['message']}")
            print()
        
        if pass_rate >= 80:
            print("🎉 EXCELLENT: System is working well!")
        elif pass_rate >= 60:
            print("⚠️  GOOD: System mostly working, some issues to address")
        else:
            print("🚨 NEEDS ATTENTION: Multiple system issues detected")
        
        print("=" * 80)
        return summary

def main():
    """Main test execution"""
    # Initialize test suite
    tester = StyleSenseTestSuite()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Save results to file
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()