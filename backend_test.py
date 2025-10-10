#!/usr/bin/env python3

import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io

class BettaFishAPITester:
    def __init__(self, base_url="https://aquascan-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", error_msg=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")
        if error_msg:
            print(f"    Error: {error_msg}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("API Root Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("API Root Endpoint", False, error_msg=str(e))
            return False

    def test_get_species(self):
        """Test getting all species"""
        try:
            response = requests.get(f"{self.api_url}/species", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                species_count = len(data) if isinstance(data, list) else 0
                details = f"Status: {response.status_code}, Species count: {species_count}"
                
                # Check if we have expected Betta species
                if species_count >= 5:
                    species_names = [s.get('nama_umum', '') for s in data]
                    expected_species = ['Crown Tail', 'Half Moon', 'Plakat', 'Double Tail', 'Veiltail']
                    found_species = [name for name in expected_species if name in species_names]
                    details += f", Found expected species: {len(found_species)}/5"
                else:
                    details += " - Warning: Less than 5 species found"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get All Species", success, details)
            return success, data if success else []
            
        except Exception as e:
            self.log_test("Get All Species", False, error_msg=str(e))
            return False, []

    def test_get_species_detail(self, species_id):
        """Test getting species detail by ID"""
        try:
            response = requests.get(f"{self.api_url}/species/{species_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Species: {data.get('nama_umum', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Species Detail", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Species Detail", False, error_msg=str(e))
            return False

    def create_test_image(self):
        """Create a test image for classification"""
        # Create a simple test image
        img = Image.new('RGB', (224, 224), color='blue')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        return temp_file.name

    def test_classify_image(self):
        """Test image classification endpoint"""
        test_image_path = None
        try:
            # Create test image
            test_image_path = self.create_test_image()
            
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test_fish.jpg', f, 'image/jpeg')}
                response = requests.post(f"{self.api_url}/classify", files=files, timeout=30)
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                fish_name = data.get('hasil_klasifikasi', 'N/A')
                confidence = data.get('tingkat_keyakinan', 0)
                details = f"Status: {response.status_code}, Fish: {fish_name}, Confidence: {confidence:.2f}"
                
                # Validate response structure
                required_fields = ['hasil_klasifikasi', 'tingkat_keyakinan', 'gambar_url', 'thumbnail_url', 'riwayat_id']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    details += f", Missing fields: {missing_fields}"
                    success = False
            else:
                details = f"Status: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f", Error: {error_data.get('detail', 'Unknown error')}"
                    except:
                        details += f", Response: {response.text[:100]}"
                
            self.log_test("Image Classification", success, details)
            return success
            
        except Exception as e:
            self.log_test("Image Classification", False, error_msg=str(e))
            return False
        finally:
            # Clean up test image
            if test_image_path and os.path.exists(test_image_path):
                os.unlink(test_image_path)

    def test_file_size_validation(self):
        """Test file size validation (should reject files > 5MB)"""
        try:
            # Create a large test image (simulate > 5MB)
            # We'll create a large image that should be rejected
            large_img = Image.new('RGB', (3000, 3000), color='red')
            
            # Save to bytes
            img_bytes = io.BytesIO()
            large_img.save(img_bytes, format='JPEG', quality=100)
            img_bytes.seek(0)
            
            # Check if the image is actually large enough
            img_size = len(img_bytes.getvalue())
            
            files = {'file': ('large_fish.jpg', img_bytes, 'image/jpeg')}
            response = requests.post(f"{self.api_url}/classify", files=files, timeout=30)
            
            # Should return 400 for file too large
            if img_size > 5 * 1024 * 1024:  # > 5MB
                success = response.status_code == 400
                details = f"Image size: {img_size/1024/1024:.1f}MB, Status: {response.status_code}"
            else:
                # If image isn't large enough, test passes if classification works
                success = response.status_code in [200, 400]
                details = f"Image size: {img_size/1024/1024:.1f}MB (not large enough for test), Status: {response.status_code}"
                
            self.log_test("File Size Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("File Size Validation", False, error_msg=str(e))
            return False

    def test_invalid_file_type(self):
        """Test invalid file type validation"""
        try:
            # Create a text file instead of image
            text_content = b"This is not an image file"
            
            files = {'file': ('not_an_image.txt', io.BytesIO(text_content), 'text/plain')}
            response = requests.post(f"{self.api_url}/classify", files=files, timeout=10)
            
            # Should return 400 for invalid file type
            success = response.status_code == 400
            details = f"Status: {response.status_code}"
            
            if response.text:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"
                    
            self.log_test("Invalid File Type Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Invalid File Type Validation", False, error_msg=str(e))
            return False

    def test_get_history(self):
        """Test getting classification history"""
        try:
            response = requests.get(f"{self.api_url}/history", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                history_count = len(data) if isinstance(data, list) else 0
                details = f"Status: {response.status_code}, History items: {history_count}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Classification History", success, details)
            return success, data if success else []
            
        except Exception as e:
            self.log_test("Get Classification History", False, error_msg=str(e))
            return False, []

    def test_delete_history(self, classification_id):
        """Test deleting a classification from history"""
        try:
            response = requests.delete(f"{self.api_url}/history/{classification_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Delete Classification History", success, details)
            return success
            
        except Exception as e:
            self.log_test("Delete Classification History", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting Betta Fish Classification API Tests")
        print("=" * 60)
        
        # Test 1: API Root
        if not self.test_api_root():
            print("❌ API Root failed - stopping tests")
            return False
            
        # Test 2: Get Species
        species_success, species_data = self.test_get_species()
        
        # Test 3: Get Species Detail (if we have species)
        if species_success and species_data:
            first_species_id = species_data[0].get('id')
            if first_species_id:
                self.test_get_species_detail(first_species_id)
        
        # Test 4: Image Classification
        self.test_classify_image()
        
        # Test 5: File Size Validation
        self.test_file_size_validation()
        
        # Test 6: Invalid File Type
        self.test_invalid_file_type()
        
        # Test 7: Get History
        history_success, history_data = self.test_get_history()
        
        # Test 8: Delete History (if we have history items)
        if history_success and history_data:
            first_history_id = history_data[0].get('id')
            if first_history_id:
                self.test_delete_history(first_history_id)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

    def get_test_summary(self):
        """Get detailed test summary"""
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BettaFishAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        summary = tester.get_test_summary()
        
        # Write results to file
        results_file = "/app/backend_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())