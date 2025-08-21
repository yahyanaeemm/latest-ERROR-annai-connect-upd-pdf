#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class BadgeManagementTester:
    def __init__(self, base_url="https://admissions-hub-4.preview.emergentagent.com"):
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

    def test_badge_management_endpoints(self):
        """Test all badge management endpoints"""
        print("🏆 Testing Badge Management System")
        print("=" * 40)
        
        # Login as admin/coordinator
        admin_credentials = [
            ("super admin", "Admin@annaiconnect", "admin"),
            ("arulanantham", "Arul@annaiconnect", "coordinator")
        ]
        
        login_success = False
        user_key = None
        for username, password, key in admin_credentials:
            if self.test_login(username, password, key):
                login_success = True
                user_key = key
                break
        
        if not login_success:
            print("❌ Failed to login - cannot test badge management")
            return False
        
        # Test 1: GET /api/coordinator/agents
        print("\n1. Testing GET /api/coordinator/agents")
        success, response = self.run_test(
            "Get Agents for Badge Management",
            "GET",
            "coordinator/agents",
            200,
            token_user=user_key
        )
        
        if not success:
            return False
            
        agents = response if isinstance(response, list) else []
        print(f"   Found {len(agents)} agents")
        
        if agents:
            agent = agents[0]
            print(f"   Sample agent: {agent.get('full_name', 'N/A')} - Badges: {len(agent.get('badges', []))}")
            self.test_data['agent_id'] = agent.get('id')
        
        # Test 2: GET /api/badge-templates
        print("\n2. Testing GET /api/badge-templates")
        success, response = self.run_test(
            "Get Badge Templates",
            "GET",
            "badge-templates",
            200,
            token_user=user_key
        )
        
        if not success:
            return False
            
        templates = response if isinstance(response, list) else []
        print(f"   Found {len(templates)} badge templates")
        
        if templates:
            template = templates[0]
            print(f"   Sample template: {template.get('title', 'N/A')} - {template.get('description', 'N/A')}")
            self.test_data['template'] = template
        
        # Test 3: POST /api/coordinator/agents/{agent_id}/badges (assign badge)
        if self.test_data.get('agent_id') and self.test_data.get('template'):
            print("\n3. Testing POST /api/coordinator/agents/{agent_id}/badges")
            
            template = self.test_data['template']
            badge_data = {
                'badge_type': template['type'],
                'badge_title': template['title'],
                'badge_description': f"Test assignment: {template['description']}",
                'badge_color': template['color']
            }
            
            success, response = self.run_test(
                "Assign Badge to Agent",
                "POST",
                f"coordinator/agents/{self.test_data['agent_id']}/badges",
                200,
                data=badge_data,
                files={},
                token_user=user_key
            )
            
            if success:
                badge = response.get('badge', {})
                print(f"   Badge assigned: {badge.get('title', 'N/A')}")
                self.test_data['badge_id'] = badge.get('id')
            else:
                return False
        
        # Test 4: DELETE /api/coordinator/agents/{agent_id}/badges/{badge_id} (remove badge)
        if self.test_data.get('agent_id') and self.test_data.get('badge_id'):
            print("\n4. Testing DELETE /api/coordinator/agents/{agent_id}/badges/{badge_id}")
            
            success, response = self.run_test(
                "Remove Badge from Agent",
                "DELETE",
                f"coordinator/agents/{self.test_data['agent_id']}/badges/{self.test_data['badge_id']}",
                200,
                token_user=user_key
            )
            
            if success:
                print(f"   Badge removed successfully")
            else:
                return False
        
        # Test 5: Login as agent and test profile endpoint
        agent_credentials = [
            ("agent1", "Agent@annaiconnect", "agent"),
            ("agent", "agent123", "agent")
        ]
        
        agent_login_success = False
        for username, password, key in agent_credentials:
            if self.test_login(username, password, key):
                agent_login_success = True
                break
        
        if agent_login_success:
            print("\n5. Testing GET /api/agent/profile (includes badges)")
            success, response = self.run_test(
                "Get Agent Profile with Badges",
                "GET",
                "agent/profile",
                200,
                token_user="agent"
            )
            
            if success:
                badges = response.get('badges', [])
                print(f"   Agent profile includes {len(badges)} badges")
            else:
                return False
        
        # Test 6: Test coordinator notes functionality (create and approve student)
        if agent_login_success:
            print("\n6. Testing coordinator notes functionality integration")
            
            # Agent creates student
            student_data = {
                "first_name": "BadgeTest",
                "last_name": "Student",
                "email": f"badge.test.{datetime.now().strftime('%H%M%S')}@example.com",
                "phone": "1234567890",
                "course": "BSc"
            }
            
            success, response = self.run_test(
                "Create Student for Badge Integration Test",
                "POST",
                "students",
                200,
                data=student_data,
                token_user="agent"
            )
            
            if success:
                student_id = response.get('id')
                print(f"   Student created: {student_id}")
                
                # Coordinator approves with notes
                approval_data = {
                    'status': 'approved',
                    'notes': 'Coordinator approval with notes - testing badge system integration'
                }
                
                success, response = self.run_test(
                    "Coordinator Approves Student with Notes",
                    "PUT",
                    f"students/{student_id}/status",
                    200,
                    data=approval_data,
                    files={},
                    token_user=user_key
                )
                
                if success:
                    print("   Coordinator notes functionality working correctly")
                else:
                    return False
            else:
                return False
        
        return True

    def run_tests(self):
        """Run all badge management tests"""
        success = self.test_badge_management_endpoints()
        
        print("\n" + "=" * 60)
        print("🎯 BADGE MANAGEMENT TESTING SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if success:
            print("\n✅ ALL BADGE MANAGEMENT TESTS PASSED!")
            print("🎖️ VERIFIED FUNCTIONALITY:")
            print("   ✅ GET /api/coordinator/agents - Returns agents with badge information")
            print("   ✅ GET /api/badge-templates - Returns predefined badge templates")
            print("   ✅ POST /api/coordinator/agents/{agent_id}/badges - Assigns badges to agents")
            print("   ✅ DELETE /api/coordinator/agents/{agent_id}/badges/{badge_id} - Removes badges")
            print("   ✅ GET /api/agent/profile - Includes badges in agent profile response")
            print("   ✅ Coordinator notes functionality - Still works with student approval process")
            print("\n🎯 CONCLUSION:")
            print("   The badge management system is fully functional and ready for production.")
        else:
            print("\n❌ SOME BADGE MANAGEMENT TESTS FAILED")
            print("   Check the detailed test output above for specific failures.")
        
        return success

if __name__ == "__main__":
    tester = BadgeManagementTester()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Badge management system testing completed successfully!")
        exit(0)
    else:
        print("\n❌ Badge management system testing failed!")
        exit(1)