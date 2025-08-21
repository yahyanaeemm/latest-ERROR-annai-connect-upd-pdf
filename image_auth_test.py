#!/usr/bin/env python3
"""
Final verification test for Complete Image Viewing Authentication Fix
This test verifies the specific requirements from the review request:
1. Authentication Test: Login as coordinator and verify access to document endpoints
2. Image Document Test: Test GET /api/students/cac25fc9-a0a1-4991-9e55-bb676df1f2ae/documents/id_proof/download 
3. PDF Document Test: Test GET /api/students/cac25fc9-a0a1-4991-9e55-bb676df1f2ae/documents/tc/download
4. Access Control: Verify authentication is still required
"""

import requests
import sys
import json
from datetime import datetime

class ImageAuthTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token_user=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add authorization if token_user specified
        if token_user and token_user in self.tokens:
            test_headers['Authorization'] = f'Bearer {self.tokens[token_user]}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password, user_key):
        """Test login and store token"""
        success, response = self.run_test(
            f"Login as {username}",
            "POST",
            "login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.tokens[user_key] = response['access_token']
            print(f"   Token stored for {user_key}")
            return True
        return False

    def test_image_viewing_authentication_fix_verification(self, coordinator_user_key):
        """Final verification test for Complete Image Viewing Authentication Fix"""
        print("\n🔍 FINAL VERIFICATION: Complete Image Viewing Authentication Fix")
        print("-" * 65)
        
        # Test 1: Authentication Test - Login as coordinator and verify access
        success, response = self.run_test(
            "Coordinator Authentication Verification",
            "GET",
            "me",
            200,
            token_user=coordinator_user_key
        )
        
        if not success:
            print("❌ Coordinator authentication failed")
            return False
            
        if response.get('role') != 'coordinator':
            print(f"❌ Expected coordinator role, got {response.get('role')}")
            return False
            
        print(f"   ✅ Coordinator authenticated: {response.get('username')}")
        
        # Test 2: Image Document Test - Test specific student document endpoint
        student_id = "cac25fc9-a0a1-4991-9e55-bb676df1f2ae"
        success, response = self.run_test(
            "Image Document Download Test (id_proof)",
            "GET",
            f"students/{student_id}/documents/id_proof/download",
            200,
            token_user=coordinator_user_key
        )
        
        if not success:
            print("❌ Image document download failed")
            return False
            
        print("   ✅ Image document (id_proof) download successful")
        
        # Test 3: PDF Document Test - Test PDF document endpoint
        success, response = self.run_test(
            "PDF Document Download Test (tc)",
            "GET",
            f"students/{student_id}/documents/tc/download",
            200,
            token_user=coordinator_user_key
        )
        
        if not success:
            print("❌ PDF document download failed")
            return False
            
        print("   ✅ PDF document (tc) download successful")
        
        # Test 4: Access Control - Verify authentication is required
        # Test without authentication token
        success, response = self.run_test(
            "Document Access Without Authentication (Should Fail)",
            "GET",
            f"students/{student_id}/documents/id_proof/download",
            403  # Should fail with 403 Forbidden
        )
        
        if not success:
            print("❌ Access control test failed - unauthenticated access should be denied")
            return False
            
        print("   ✅ Access control working - unauthenticated requests properly denied")
        
        # Test 5: Agent access control (agents should not have access to document viewing)
        if 'agent1' in self.tokens:
            success, response = self.run_test(
                "Agent Access to Document Download (Should Fail)",
                "GET",
                f"students/{student_id}/documents/id_proof/download",
                403,
                token_user='agent1'
            )
            
            if not success:
                print("❌ Agent access control failed")
                return False
                
            print("   ✅ Agent access properly denied (403 status)")
        
        # Test 6: Verify document endpoints are working for coordinators
        success, response = self.run_test(
            "Get Student Documents List",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user=coordinator_user_key
        )
        
        if not success:
            print("❌ Student documents list failed")
            return False
            
        documents = response.get('documents', [])
        print(f"   ✅ Found {len(documents)} documents for student")
        
        # Verify document structure
        for doc in documents:
            if not all(key in doc for key in ['type', 'download_url', 'exists']):
                print("❌ Document structure missing required fields")
                return False
                
        print("   ✅ Document structure validation passed")
        
        return True

def main():
    """Main test execution for Image Viewing Authentication Fix verification"""
    print("🎯 FINAL VERIFICATION: Complete Image Viewing Authentication Fix")
    print("=" * 70)
    
    tester = ImageAuthTester()
    
    # Login coordinator user with specific credentials from review request
    print("\n🔐 AUTHENTICATION TESTING")
    print("-" * 30)
    
    login_success = tester.test_login("arulanantham", "Arul@annaiconnect", "coordinator")
    
    if not login_success:
        print("❌ Coordinator login failed")
        return False
    
    # Also login agent for access control testing
    if not tester.test_login("agent1", "agent123", "agent1"):
        print("⚠️ Agent login failed - access control test will be limited")
    
    # Run the specific verification test
    verification_passed = tester.test_image_viewing_authentication_fix_verification("coordinator")
    
    # Print final summary
    print("\n" + "="*70)
    print("🎯 FINAL VERIFICATION SUMMARY")
    print("="*70)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if verification_passed:
        print("\n🎉 IMAGE VIEWING AUTHENTICATION FIX VERIFICATION PASSED!")
        print("✅ Backend is working properly after frontend changes")
        print("✅ Authentication is still required for document access")
        print("✅ Image and PDF document downloads working correctly")
        print("✅ Access control properly implemented")
        return True
    else:
        print("\n❌ Image viewing authentication fix verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)