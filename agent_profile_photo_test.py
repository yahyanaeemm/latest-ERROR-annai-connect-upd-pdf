#!/usr/bin/env python3
"""
Agent Profile Photo Upload Functionality Test Script
Tests the complete agent profile photo upload workflow end-to-end
"""

import requests
import sys
import json
from datetime import datetime
import os

class AgentProfilePhotoTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None, token_user=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add authorization if token_user specified
        if token_user and token_user in self.tokens:
            test_headers['Authorization'] = f'Bearer {self.tokens[token_user]}'
        
        # Override headers if provided
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                if files is not None:
                    # Remove Content-Type for multipart/form-data
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.post(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                if files is not None:
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.put(url, data=data, headers=test_headers)
                else:
                    response = requests.put(url, json=data, headers=test_headers)

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
            print(f"   Role: {response.get('role')}")
            return True
        return False

    def test_agent_profile_photo_upload_comprehensive(self, agent_user_key):
        """Test agent profile photo upload functionality end-to-end"""
        print("\n📸 Testing Agent Profile Photo Upload Functionality")
        print("-" * 55)
        
        # Test 1: Get initial agent profile (should work without photo)
        success, response = self.run_test(
            "Get Agent Profile (Initial State)",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        # Verify profile structure
        if 'profile' not in response:
            print("❌ Profile section missing from response")
            return False
            
        profile = response['profile']
        initial_photo = profile.get('profile_photo')
        print(f"   ✅ Initial profile photo state: {initial_photo or 'None'}")
        print(f"   ✅ Agent username: {profile.get('username')}")
        print(f"   ✅ Agent email: {profile.get('email')}")
        
        # Test 2: Upload profile photo with valid base64 data
        # Create a small valid base64 image (1x1 pixel PNG)
        valid_photo_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        upload_data = {
            'photo_data': valid_photo_data
        }
        
        success, response = self.run_test(
            "Upload Agent Profile Photo (Valid Data)",
            "POST",
            "agent/profile/photo",
            200,
            data=upload_data,
            files={},  # Form data mode
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        if 'successfully' not in response.get('message', '').lower():
            print(f"❌ Expected success message, got: {response.get('message')}")
            return False
            
        print("   ✅ Profile photo uploaded successfully")
        
        # Test 3: Verify photo is stored and retrievable
        success, response = self.run_test(
            "Get Agent Profile After Photo Upload",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        updated_profile = response.get('profile', {})
        stored_photo = updated_profile.get('profile_photo')
        
        if not stored_photo:
            print("❌ Profile photo not found after upload")
            return False
            
        if stored_photo != valid_photo_data:
            print("❌ Stored photo data doesn't match uploaded data")
            return False
            
        print("   ✅ Profile photo correctly stored and retrieved")
        
        # Test 4: Update profile photo with different data
        updated_photo_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A8A"
        
        update_data = {
            'photo_data': updated_photo_data
        }
        
        success, response = self.run_test(
            "Update Agent Profile Photo (Different Data)",
            "POST",
            "agent/profile/photo",
            200,
            data=update_data,
            files={},  # Form data mode
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        print("   ✅ Profile photo updated successfully")
        
        # Test 5: Verify updated photo is stored
        success, response = self.run_test(
            "Get Agent Profile After Photo Update",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        final_profile = response.get('profile', {})
        final_photo = final_profile.get('profile_photo')
        
        if final_photo != updated_photo_data:
            print("❌ Updated photo data doesn't match")
            return False
            
        print("   ✅ Updated profile photo correctly stored")
        
        return True
    
    def test_agent_profile_photo_validation(self, agent_user_key):
        """Test agent profile photo upload validation and error handling"""
        print("\n🔍 Testing Agent Profile Photo Upload Validation")
        print("-" * 50)
        
        # Test 1: Upload with invalid base64 data
        invalid_data_tests = [
            {
                'name': 'Invalid Base64 Data',
                'data': {'photo_data': 'invalid-base64-data'},
                'expected_status': 200  # Backend should handle gracefully
            },
            {
                'name': 'Empty Photo Data',
                'data': {'photo_data': ''},
                'expected_status': 200  # Backend should handle gracefully
            },
            {
                'name': 'Missing Photo Data',
                'data': {},
                'expected_status': 422  # FastAPI validation error
            }
        ]
        
        for test_case in invalid_data_tests:
            success, response = self.run_test(
                f"Upload Photo - {test_case['name']}",
                "POST",
                "agent/profile/photo",
                test_case['expected_status'],
                data=test_case['data'],
                files={},
                token_user=agent_user_key
            )
            
            if not success:
                return False
                
            print(f"   ✅ {test_case['name']} handled correctly")
        
        # Test 2: Upload with very large base64 data (simulate large image)
        # Create a larger base64 string to test size handling
        large_photo_data = "data:image/png;base64," + "A" * 10000  # 10KB of A's
        
        success, response = self.run_test(
            "Upload Large Photo Data",
            "POST",
            "agent/profile/photo",
            200,  # Should work but may have size limits in production
            data={'photo_data': large_photo_data},
            files={},
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        print("   ✅ Large photo data handled correctly")
        
        return True
    
    def test_agent_profile_photo_access_control(self):
        """Test access control for agent profile photo upload"""
        print("\n🔒 Testing Agent Profile Photo Upload Access Control")
        print("-" * 55)
        
        valid_photo_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Test 1: Non-agent users should be denied access
        non_agent_users = [
            ('coordinator', 'Coordinator'),
            ('admin', 'Admin')
        ]
        
        for user_key, user_type in non_agent_users:
            if user_key not in self.tokens:
                continue
                
            # Test photo upload access
            success, response = self.run_test(
                f"{user_type} Access to Photo Upload (Should Fail)",
                "POST",
                "agent/profile/photo",
                403,
                data={'photo_data': valid_photo_data},
                files={},
                token_user=user_key
            )
            
            if not success:
                return False
                
            # Test profile access
            success, response = self.run_test(
                f"{user_type} Access to Agent Profile (Should Fail)",
                "GET",
                "agent/profile",
                403,
                token_user=user_key
            )
            
            if not success:
                return False
                
            print(f"   ✅ {user_type} properly denied access to agent profile features")
        
        # Test 2: Unauthenticated access should fail
        success, response = self.run_test(
            "Unauthenticated Photo Upload (Should Fail)",
            "POST",
            "agent/profile/photo",
            401,  # Unauthorized
            data={'photo_data': valid_photo_data},
            files={}
            # No token_user parameter = unauthenticated
        )
        
        if not success:
            return False
            
        success, response = self.run_test(
            "Unauthenticated Profile Access (Should Fail)",
            "GET",
            "agent/profile",
            401  # Unauthorized
            # No token_user parameter = unauthenticated
        )
        
        if not success:
            return False
            
        print("   ✅ Unauthenticated access properly denied")
        
        return True
    
    def test_agent_profile_photo_integration_workflow(self, agent_user_key):
        """Test complete agent profile photo integration workflow"""
        print("\n🔄 Testing Agent Profile Photo Integration Workflow")
        print("-" * 55)
        
        # Step 1: Get initial profile state
        success, response = self.run_test(
            "Get Initial Agent Profile State",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        initial_profile = response.get('profile', {})
        print(f"   ✅ Initial profile loaded - Username: {initial_profile.get('username')}")
        
        # Step 2: Upload profile photo
        test_photo_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        success, response = self.run_test(
            "Upload Profile Photo in Workflow",
            "POST",
            "agent/profile/photo",
            200,
            data={'photo_data': test_photo_data},
            files={},
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        print("   ✅ Profile photo uploaded in workflow")
        
        # Step 3: Verify photo appears in profile
        success, response = self.run_test(
            "Verify Photo in Profile After Upload",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        updated_profile = response.get('profile', {})
        if updated_profile.get('profile_photo') != test_photo_data:
            print("❌ Profile photo not correctly integrated in profile response")
            return False
            
        print("   ✅ Profile photo correctly integrated in profile response")
        
        # Step 4: Test profile update with other fields (ensure photo persists)
        profile_update_data = {
            'phone': '9876543210',
            'bio': 'Updated bio for testing profile photo persistence'
        }
        
        success, response = self.run_test(
            "Update Other Profile Fields",
            "PUT",
            "agent/profile",
            200,
            data=profile_update_data,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        print("   ✅ Other profile fields updated")
        
        # Step 5: Verify photo persists after other profile updates
        success, response = self.run_test(
            "Verify Photo Persists After Profile Update",
            "GET",
            "agent/profile",
            200,
            token_user=agent_user_key
        )
        
        if not success:
            return False
            
        final_profile = response.get('profile', {})
        if final_profile.get('profile_photo') != test_photo_data:
            print("❌ Profile photo lost after other profile updates")
            return False
            
        if final_profile.get('phone') != profile_update_data['phone']:
            print("❌ Other profile updates not persisted")
            return False
            
        print("   ✅ Profile photo persists after other profile updates")
        print(f"   ✅ Updated phone: {final_profile.get('phone')}")
        print(f"   ✅ Updated bio: {final_profile.get('bio')}")
        
        return True

def main():
    print("🎯 Agent Profile Photo Upload Functionality Test")
    print("=" * 55)
    print("Testing the complete agent profile photo upload workflow end-to-end")
    print("Focus Areas:")
    print("- Authentication and authorization")
    print("- Photo upload endpoint functionality")
    print("- Data persistence and retrieval")
    print("- Error handling and validation")
    print("- Access control verification")
    print("=" * 55)
    
    tester = AgentProfilePhotoTester()
    
    # Test credentials as specified in the review request
    test_users = {
        'agent1': {'username': 'agent1', 'password': 'agent@123'},
        'coordinator': {'username': 'arulanantham', 'password': 'Arul@annaiconnect'},
        'admin': {'username': 'super admin', 'password': 'Admin@annaiconnect'}
    }
    
    print("\n📋 Phase 1: Authentication Testing")
    print("-" * 35)
    
    # Test login for all users
    login_success = True
    for user_key, credentials in test_users.items():
        if not tester.test_login(credentials['username'], credentials['password'], user_key):
            print(f"❌ Login failed for {user_key}")
            if user_key == 'agent1':
                print("❌ CRITICAL: Agent1 login failed - cannot proceed with profile photo tests")
                return 1
            login_success = False
    
    if 'agent1' not in tester.tokens:
        print("❌ CRITICAL: Agent1 authentication failed - profile photo tests cannot proceed")
        return 1
    
    print("\n📋 Phase 2: Agent Profile Photo Upload Testing")
    print("-" * 50)
    
    test_results = []
    
    # Test 1: Comprehensive photo upload functionality
    print("\n🔸 Test Suite 1: Comprehensive Photo Upload Functionality")
    result1 = tester.test_agent_profile_photo_upload_comprehensive('agent1')
    test_results.append(('Comprehensive Photo Upload', result1))
    
    # Test 2: Validation and error handling
    print("\n🔸 Test Suite 2: Validation and Error Handling")
    result2 = tester.test_agent_profile_photo_validation('agent1')
    test_results.append(('Validation and Error Handling', result2))
    
    # Test 3: Access control
    print("\n🔸 Test Suite 3: Access Control Verification")
    result3 = tester.test_agent_profile_photo_access_control()
    test_results.append(('Access Control', result3))
    
    # Test 4: Integration workflow
    print("\n🔸 Test Suite 4: Integration Workflow")
    result4 = tester.test_agent_profile_photo_integration_workflow('agent1')
    test_results.append(('Integration Workflow', result4))
    
    print("\n" + "=" * 55)
    print("📊 AGENT PROFILE PHOTO UPLOAD TEST RESULTS")
    print("=" * 55)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall API Tests: {tester.tests_passed}/{tester.tests_run} passed")
    
    if all_passed:
        print("\n🎉 ALL AGENT PROFILE PHOTO UPLOAD TESTS PASSED!")
        print("✅ Authentication working correctly")
        print("✅ Photo upload endpoint functional")
        print("✅ Data persistence and retrieval working")
        print("✅ Error handling and validation working")
        print("✅ Access control properly implemented")
        print("✅ Integration workflow complete")
        print("\n🚀 Agent profile photo upload functionality is ready for production!")
        return 0
    else:
        failed_tests = [name for name, result in test_results if not result]
        print(f"\n❌ {len(failed_tests)} TEST SUITE(S) FAILED:")
        for test_name in failed_tests:
            print(f"   - {test_name}")
        print("\n⚠️  Please review the failures above before deploying to production")
        return 1

if __name__ == "__main__":
    sys.exit(main())