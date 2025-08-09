#!/usr/bin/env python3

import requests
import json
import sys

class CoordinatorDashboardTester:
    def __init__(self, base_url="https://0852e42c-8e90-4ca2-b475-b2bbf75ea44e.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, token_user=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if token_user and token_user in self.tokens:
            test_headers['Authorization'] = f'Bearer {self.tokens[token_user]}'
        
        if headers:
            test_headers.update(headers)

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

    def test_coordinator_dashboard_routing_fix(self):
        """Test the critical routing fix for coordinator dashboard APIs"""
        print("\n🚀 TESTING COORDINATOR DASHBOARD ROUTING FIX")
        print("=" * 60)
        
        # Test 1: GET /api/students/dropdown - Should work correctly now
        print("\n📋 PRIORITY TEST 1: Students Dropdown API")
        print("-" * 45)
        
        success, response = self.run_test(
            "GET /api/students/dropdown (Coordinator)",
            "GET",
            "students/dropdown",
            200,
            token_user='coordinator'
        )
        
        if not success:
            print("❌ CRITICAL: Dropdown endpoint still not working!")
            return False
            
        if not isinstance(response, list):
            print("❌ CRITICAL: Response should be a list")
            return False
            
        print(f"   ✅ Found {len(response)} students in dropdown")
        
        if response:
            first_student = response[0]
            required_fields = ['id', 'name', 'token_number', 'course', 'status']
            for field in required_fields:
                if field not in first_student:
                    print(f"❌ Missing field '{field}' in dropdown item")
                    return False
                    
            print(f"   ✅ Sample: {first_student['name']} - {first_student['token_number']} - {first_student['course']}")
            student_id = first_student['id']
        else:
            print("❌ No students found in dropdown")
            return False

        # Test 2: GET /api/students/{student_id}/detailed - Should work with proper student IDs
        print("\n👤 PRIORITY TEST 2: Student Detailed API")
        print("-" * 45)
        
        success, response = self.run_test(
            f"GET /api/students/{student_id}/detailed (Coordinator)",
            "GET",
            f"students/{student_id}/detailed",
            200,
            token_user='coordinator'
        )
        
        if not success:
            print("❌ CRITICAL: Detailed endpoint not working!")
            return False
            
        # Verify comprehensive student data
        required_fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'course', 'status', 'token_number']
        for field in required_fields:
            if field not in response:
                print(f"❌ Missing field '{field}' in detailed response")
                return False
                
        print(f"   ✅ Student: {response['first_name']} {response['last_name']} - {response['course']}")
        
        # Verify agent_info is included
        if 'agent_info' not in response:
            print("❌ Missing 'agent_info' field")
            return False
            
        print("   ✅ Agent info included")

        # Test 3: GET /api/students/{student_id}/documents - Should work with proper student IDs
        print("\n📄 PRIORITY TEST 3: Student Documents API")
        print("-" * 45)
        
        success, response = self.run_test(
            f"GET /api/students/{student_id}/documents (Coordinator)",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user='coordinator'
        )
        
        if not success:
            print("❌ CRITICAL: Documents endpoint not working!")
            return False
            
        # Verify response structure
        if 'student_id' not in response or 'documents' not in response:
            print("❌ Missing required fields in documents response")
            return False
            
        if response['student_id'] != student_id:
            print("❌ Student ID mismatch")
            return False
            
        print(f"   ✅ Found {len(response['documents'])} documents")
        
        return True

    def test_access_control(self):
        """Test access control for coordinator dashboard APIs"""
        print("\n🔒 ACCESS CONTROL VERIFICATION")
        print("-" * 40)
        
        # Test coordinator access (should work)
        print("\n   Testing COORDINATOR access (should work):")
        success = self.test_coordinator_dashboard_routing_fix()
        if not success:
            return False
        
        # Test admin access (should work)
        print("\n   Testing ADMIN access (should work):")
        success, response = self.run_test(
            "GET /api/students/dropdown (Admin)",
            "GET",
            "students/dropdown",
            200,
            token_user='admin'
        )
        if not success:
            return False
        print("   ✅ Admin access working")
        
        # Test agent access (should fail with 403)
        print("\n   Testing AGENT access (should fail with 403):")
        success, response = self.run_test(
            "GET /api/students/dropdown (Agent - Should Fail)",
            "GET",
            "students/dropdown",
            403,
            token_user='agent1'
        )
        if not success:
            return False
        print("   ✅ Agent properly denied access")
        
        return True

    def test_regression_verification(self):
        """Test that existing endpoints still work"""
        print("\n🔄 REGRESSION TESTING")
        print("-" * 30)
        
        # Verify existing /api/students endpoint still works
        success, response = self.run_test(
            "Existing /api/students endpoint",
            "GET",
            "students",
            200,
            token_user='coordinator'
        )
        if not success:
            return False
        print("   ✅ Existing students endpoint working")
        
        # Verify existing /api/students/{id} endpoint still works
        if response:
            student_id = response[0]['id']
            success, response = self.run_test(
                "Existing /api/students/{id} endpoint",
                "GET",
                f"students/{student_id}",
                200,
                token_user='coordinator'
            )
            if not success:
                return False
            print("   ✅ Existing student by ID endpoint working")
        
        return True

    def test_complete_workflow(self):
        """Test complete coordinator dashboard workflow"""
        print("\n🔄 COMPLETE WORKFLOW TEST")
        print("-" * 35)
        
        # Step 1: Login as coordinator
        print("Step 1: Login as coordinator")
        if not self.test_login('coordinator', 'coord123', 'coordinator'):
            return False
        
        # Step 2: Call /api/students/dropdown to get student list
        print("Step 2: Get students dropdown")
        success, dropdown_response = self.run_test(
            "Get Students Dropdown",
            "GET",
            "students/dropdown",
            200,
            token_user='coordinator'
        )
        if not success or not dropdown_response:
            return False
        
        # Step 3: Pick a student ID from dropdown response
        student_id = dropdown_response[0]['id']
        print(f"Step 3: Selected student ID: {student_id}")
        
        # Step 4: Call /api/students/{student_id}/detailed with that ID
        print("Step 4: Get detailed student info")
        success, detailed_response = self.run_test(
            "Get Student Detailed Info",
            "GET",
            f"students/{student_id}/detailed",
            200,
            token_user='coordinator'
        )
        if not success:
            return False
        
        # Step 5: Call /api/students/{student_id}/documents with that ID
        print("Step 5: Get student documents")
        success, documents_response = self.run_test(
            "Get Student Documents",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user='coordinator'
        )
        if not success:
            return False
        
        # Step 6: Verify data flows correctly between endpoints
        print("Step 6: Verify data consistency")
        if detailed_response['id'] != student_id:
            print("❌ Student ID mismatch between endpoints")
            return False
        
        if documents_response['student_id'] != student_id:
            print("❌ Student ID mismatch in documents")
            return False
        
        print("   ✅ Complete workflow successful!")
        return True

def main():
    print("🚀 COORDINATOR DASHBOARD ROUTING FIX VERIFICATION")
    print("=" * 60)
    
    tester = CoordinatorDashboardTester()
    
    # Test credentials
    test_users = {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'coordinator': {'username': 'coordinator', 'password': 'coord123'},
        'agent1': {'username': 'agent1', 'password': 'agent123'}
    }
    
    print("\n📋 Phase 1: Authentication")
    print("-" * 30)
    
    # Test login for all users
    for user_key, credentials in test_users.items():
        if not tester.test_login(credentials['username'], credentials['password'], user_key):
            print(f"❌ Login failed for {user_key}")
            return 1
    
    print("\n📋 Phase 2: Complete Workflow Test")
    print("-" * 30)
    
    if not tester.test_complete_workflow():
        print("❌ Complete workflow test failed")
        return 1
    
    print("\n📋 Phase 3: Access Control Verification")
    print("-" * 30)
    
    if not tester.test_access_control():
        print("❌ Access control test failed")
        return 1
    
    print("\n📋 Phase 4: Regression Testing")
    print("-" * 30)
    
    if not tester.test_regression_verification():
        print("❌ Regression test failed")
        return 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL COORDINATOR DASHBOARD ROUTING TESTS PASSED!")
        print("\n✅ ROUTING FIX VERIFICATION SUCCESSFUL:")
        print("   • GET /api/students/dropdown - Working correctly")
        print("   • GET /api/students/{id}/detailed - Working correctly") 
        print("   • GET /api/students/{id}/documents - Working correctly")
        print("   • Access control working (coordinator/admin: 200, agent: 403)")
        print("   • No conflicts with existing endpoints")
        print("   • Complete workflow functional")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())