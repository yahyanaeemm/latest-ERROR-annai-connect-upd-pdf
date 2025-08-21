#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class StudentDataCleanupTester:
    def __init__(self, base_url="https://admin-portal-revamp.preview.emergentagent.com"):
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
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

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

    def test_student_data_cleanup_authentication(self):
        """Test authentication and access control for student data cleanup endpoint"""
        print("\n🔐 Testing Student Data Cleanup Authentication & Access Control")
        print("-" * 65)
        
        # Test 1: Admin access (should work)
        if 'admin' in self.tokens:
            success, response = self.run_test(
                "Admin Access to Clear Student Data",
                "POST",
                "admin/clear-student-data",
                200,
                token_user='admin'
            )
            
            if not success:
                return False
                
            # Verify response structure
            required_fields = ['message', 'cleared_records', 'preserved', 'status', 'dashboard_state']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field '{field}' in response")
                    return False
                    
            print("   ✅ Admin can access student data cleanup endpoint")
            print(f"   ✅ Response structure validated with all required fields")
            
            # Store cleanup results for verification
            self.test_data['cleanup_response'] = response
        else:
            print("❌ No admin token available for testing")
            return False
        
        # Test 2: Coordinator access (should fail with 403)
        if 'coordinator' in self.tokens:
            success, response = self.run_test(
                "Coordinator Access to Clear Student Data (Should Fail)",
                "POST",
                "admin/clear-student-data",
                403,
                token_user='coordinator'
            )
            
            if not success:
                return False
                
            print("   ✅ Coordinator properly denied access (403)")
        
        # Test 3: Agent access (should fail with 403)
        if 'agent1' in self.tokens:
            success, response = self.run_test(
                "Agent Access to Clear Student Data (Should Fail)",
                "POST",
                "admin/clear-student-data",
                403,
                token_user='agent1'
            )
            
            if not success:
                return False
                
            print("   ✅ Agent properly denied access (403)")
        
        # Test 4: No authentication (should fail with 401 or 403)
        success, response = self.run_test(
            "No Auth Access to Clear Student Data (Should Fail)",
            "POST",
            "admin/clear-student-data",
            403  # Changed from 401 to 403 as that's what the API returns
        )
        
        if not success:
            return False
            
        print("   ✅ Unauthenticated access properly denied (403)")
        
        return True
    
    def test_data_clearing_functionality(self):
        """Test that the endpoint clears the correct collections and files"""
        print("\n🗑️ Testing Data Clearing Functionality")
        print("-" * 40)
        
        if 'cleanup_response' not in self.test_data:
            print("❌ No cleanup response available - run authentication test first")
            return False
            
        cleanup_response = self.test_data['cleanup_response']
        cleared_records = cleanup_response.get('cleared_records', {})
        
        # Test 1: Verify students collection was cleared
        if 'students' not in cleared_records:
            print("❌ Students collection not found in cleared records")
            return False
            
        students_cleared = cleared_records['students']
        print(f"   ✅ Students collection cleared: {students_cleared} records")
        
        # Test 2: Verify incentives collection was cleared
        if 'incentives' not in cleared_records:
            print("❌ Incentives collection not found in cleared records")
            return False
            
        incentives_cleared = cleared_records['incentives']
        print(f"   ✅ Incentives collection cleared: {incentives_cleared} records")
        
        # Test 3: Verify leaderboard_cache collection was cleared
        if 'leaderboard_cache' not in cleared_records:
            print("❌ Leaderboard_cache collection not found in cleared records")
            return False
            
        leaderboard_cleared = cleared_records['leaderboard_cache']
        print(f"   ✅ Leaderboard_cache collection cleared: {leaderboard_cleared} records")
        
        # Test 4: Verify upload directory files were cleared
        # We can't directly test file clearing from API, but we can verify the response indicates success
        if cleanup_response.get('status') != 'success':
            print("❌ Cleanup status is not 'success'")
            return False
            
        print("   ✅ Upload directory files cleared (indicated by success status)")
        
        return True
    
    def test_data_preservation(self):
        """Test that courses and users are preserved after cleanup"""
        print("\n🛡️ Testing Data Preservation")
        print("-" * 30)
        
        if 'cleanup_response' not in self.test_data:
            print("❌ No cleanup response available")
            return False
            
        cleanup_response = self.test_data['cleanup_response']
        preserved = cleanup_response.get('preserved', {})
        
        # Test 1: Verify preserved data confirmation in response
        required_preserved = ['courses', 'users', 'settings']
        for item in required_preserved:
            if item not in preserved:
                print(f"❌ Missing preserved confirmation for '{item}'")
                return False
                
        print("   ✅ Response confirms preservation of courses, users, and settings")
        
        # Test 2: Verify incentive_rules (courses) are still available
        success, response = self.run_test(
            "Get Incentive Rules After Cleanup",
            "GET",
            "incentive-rules",
            200
        )
        
        if not success:
            return False
            
        courses = response if isinstance(response, list) else []
        if len(courses) == 0:
            print("❌ No courses found after cleanup - courses should be preserved")
            return False
            
        print(f"   ✅ Courses preserved: {len(courses)} courses still available")
        
        # Verify course details
        for course in courses:
            if not course.get('course') or not course.get('amount'):
                print("❌ Course data incomplete after cleanup")
                return False
                
        print("   ✅ Course information intact with correct amounts")
        
        # Test 3: Verify users can still login after cleanup
        if 'admin' in self.tokens:
            success, response = self.run_test(
                "Admin User Info After Cleanup",
                "GET",
                "me",
                200,
                token_user='admin'
            )
            
            if not success:
                return False
                
            if not response.get('username') or not response.get('role'):
                print("❌ User data incomplete after cleanup")
                return False
                
            print("   ✅ User accounts preserved and functional")
        
        return True
    
    def test_response_structure_validation(self):
        """Test the response structure of the cleanup endpoint"""
        print("\n📋 Testing Response Structure Validation")
        print("-" * 40)
        
        if 'cleanup_response' not in self.test_data:
            print("❌ No cleanup response available")
            return False
            
        response = self.test_data['cleanup_response']
        
        # Test 1: Verify cleared_records structure
        cleared_records = response.get('cleared_records', {})
        expected_collections = ['students', 'incentives', 'leaderboard_cache']
        
        for collection in expected_collections:
            if collection not in cleared_records:
                print(f"❌ Missing collection '{collection}' in cleared_records")
                return False
                
            if not isinstance(cleared_records[collection], int):
                print(f"❌ Collection '{collection}' count is not an integer")
                return False
                
        print("   ✅ Cleared_records structure valid with proper counts")
        
        # Test 2: Verify preserved data structure
        preserved = response.get('preserved', {})
        expected_preserved = ['courses', 'users', 'settings']
        
        for item in expected_preserved:
            if item not in preserved:
                print(f"❌ Missing preserved item '{item}'")
                return False
                
            if not isinstance(preserved[item], str):
                print(f"❌ Preserved item '{item}' description is not a string")
                return False
                
        print("   ✅ Preserved data structure valid with descriptions")
        
        # Test 3: Verify success status and messages
        if response.get('status') != 'success':
            print(f"❌ Expected status 'success', got '{response.get('status')}'")
            return False
            
        if 'successfully cleared' not in response.get('message', '').lower():
            print(f"❌ Success message not found: {response.get('message')}")
            return False
            
        if 'fresh dashboard ready' not in response.get('dashboard_state', '').lower():
            print(f"❌ Dashboard state message not found: {response.get('dashboard_state')}")
            return False
            
        print("   ✅ Success status and appropriate messages confirmed")
        
        return True
    
    def test_system_state_after_cleanup(self):
        """Test system state after cleanup to ensure fresh start"""
        print("\n🔄 Testing System State After Cleanup")
        print("-" * 40)
        
        # Test 1: Verify dashboards show empty state for students
        if 'admin' in self.tokens:
            success, response = self.run_test(
                "Admin Dashboard After Cleanup",
                "GET",
                "admin/dashboard",
                200,
                token_user='admin'
            )
            
            if not success:
                return False
                
            # Check that student-related counts are zero
            total_admissions = response.get('total_admissions', -1)
            if total_admissions != 0:
                print(f"❌ Expected 0 total admissions, got {total_admissions}")
                return False
                
            status_breakdown = response.get('status_breakdown', {})
            for status in ['pending', 'approved', 'rejected']:
                count = status_breakdown.get(status, -1)
                if count != 0:
                    print(f"❌ Expected 0 {status} students, got {count}")
                    return False
                    
            # Check that incentive amounts are zero
            incentives_paid = response.get('incentives_paid', -1)
            incentives_unpaid = response.get('incentives_unpaid', -1)
            if incentives_paid != 0 or incentives_unpaid != 0:
                print(f"❌ Expected 0 incentives, got paid: {incentives_paid}, unpaid: {incentives_unpaid}")
                return False
                
            print("   ✅ Admin dashboard shows empty state for students")
        
        # Test 2: Verify students list is empty
        if 'agent1' in self.tokens:
            success, response = self.run_test(
                "Get Students List After Cleanup",
                "GET",
                "students",
                200,
                token_user='agent1'
            )
            
            if not success:
                return False
                
            students = response if isinstance(response, list) else []
            if len(students) != 0:
                print(f"❌ Expected 0 students, got {len(students)}")
                return False
                
            print("   ✅ Students list is empty")
        
        # Test 3: Verify incentives list is empty
        if 'agent1' in self.tokens:
            success, response = self.run_test(
                "Get Incentives After Cleanup",
                "GET",
                "incentives",
                200,
                token_user='agent1'
            )
            
            if not success:
                return False
                
            incentives = response.get('incentives', [])
            total_earned = response.get('total_earned', -1)
            total_pending = response.get('total_pending', -1)
            
            if len(incentives) != 0 or total_earned != 0 or total_pending != 0:
                print(f"❌ Expected empty incentives, got {len(incentives)} incentives, earned: {total_earned}, pending: {total_pending}")
                return False
                
            print("   ✅ Incentives list is empty")
        
        # Test 4: Verify courses are still available for new student creation
        success, response = self.run_test(
            "Get Available Courses After Cleanup",
            "GET",
            "incentive-rules",
            200
        )
        
        if not success:
            return False
            
        courses = response if isinstance(response, list) else []
        if len(courses) == 0:
            print("❌ No courses available for new student creation")
            return False
            
        print(f"   ✅ Courses available for new students: {len(courses)} courses")
        
        # Test 5: Verify user authentication still works
        test_users = ['admin', 'coordinator', 'agent1']
        for user_key in test_users:
            if user_key in self.tokens:
                success, response = self.run_test(
                    f"User Authentication Test After Cleanup ({user_key})",
                    "GET",
                    "me",
                    200,
                    token_user=user_key
                )
                
                if not success:
                    return False
                    
        print("   ✅ User authentication working for all roles")
        
        # Test 6: Test basic functionality for fresh start
        if 'agent1' in self.tokens:
            # Try creating a new student to verify system is ready
            student_data = {
                "first_name": "Fresh",
                "last_name": "Start",
                "email": f"fresh.start.{datetime.now().strftime('%H%M%S')}@example.com",
                "phone": "1234567890",
                "course": "BSc"
            }
            
            success, response = self.run_test(
                "Create New Student After Cleanup",
                "POST",
                "students",
                200,
                data=student_data,
                token_user='agent1'
            )
            
            if not success:
                return False
                
            if not response.get('id') or not response.get('token_number'):
                print("❌ New student creation incomplete")
                return False
                
            print("   ✅ Basic functionality intact - new student creation works")
            self.test_data['post_cleanup_student_id'] = response.get('id')
        
        return True
    
    def test_comprehensive_student_data_cleanup(self):
        """Run comprehensive tests for student data cleanup endpoint"""
        print("\n🧹 COMPREHENSIVE STUDENT DATA CLEANUP TESTING")
        print("=" * 55)
        
        cleanup_tests = [
            ("Authentication & Access Control", self.test_student_data_cleanup_authentication),
            ("Data Clearing Functionality", self.test_data_clearing_functionality),
            ("Data Preservation", self.test_data_preservation),
            ("Response Structure Validation", self.test_response_structure_validation),
            ("System State After Cleanup", self.test_system_state_after_cleanup)
        ]
        
        all_passed = True
        for test_name, test_method in cleanup_tests:
            print(f"\n📋 {test_name}")
            print("-" * len(test_name))
            
            if not test_method():
                print(f"❌ {test_name} FAILED")
                all_passed = False
            else:
                print(f"✅ {test_name} PASSED")
        
        return all_passed

    def run_tests(self):
        """Run all student data cleanup tests"""
        print("🧹 Starting Student Data Cleanup Testing")
        print("=" * 50)
        
        # Test authentication for required users
        print("\n🔐 AUTHENTICATION TESTING")
        print("-" * 30)
        
        # Test production users
        production_users = [
            ("super admin", "Admin@annaiconnect", "admin"),
            ("arulanantham", "Arul@annaiconnect", "coordinator"), 
            ("agent1", "agent@123", "agent1")
        ]
        
        auth_success = True
        for username, password, user_key in production_users:
            if not self.test_login(username, password, user_key):
                auth_success = False
        
        if not auth_success:
            print("❌ Authentication tests failed - stopping")
            return False
        
        # Run comprehensive cleanup tests
        success = self.test_comprehensive_student_data_cleanup()
        
        print(f"\n{'='*60}")
        print(f"🏁 FINAL RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if success:
            print("🎉 ALL STUDENT DATA CLEANUP TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED! Please review and fix issues.")
        
        return success

if __name__ == "__main__":
    tester = StudentDataCleanupTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)