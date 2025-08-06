import requests
import sys
import json
from datetime import datetime
import os
import tempfile

class AdmissionSystemAPITester:
    def __init__(self, base_url="https://b6c6207b-e607-41c9-b324-aebdf6793677.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}  # Store tokens for different users
        self.test_data = {}  # Store created test data
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
                if files:
                    # Remove Content-Type for multipart/form-data
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.post(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                if files is not None:  # Check for None specifically, not just falsy
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
            return True
        return False

    def test_user_info(self, user_key):
        """Test getting current user info"""
        success, response = self.run_test(
            f"Get user info for {user_key}",
            "GET",
            "me",
            200,
            token_user=user_key
        )
        if success:
            print(f"   User: {response.get('username')} - Role: {response.get('role')}")
        return success

    def test_create_student(self, user_key):
        """Test creating a student"""
        student_data = {
            "first_name": "Test",
            "last_name": "Student",
            "email": f"test.student.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "1234567890",
            "course": "BSc"
        }
        
        success, response = self.run_test(
            "Create Student",
            "POST",
            "students",
            200,
            data=student_data,
            token_user=user_key
        )
        
        if success and 'id' in response:
            self.test_data['student_id'] = response['id']
            self.test_data['token_number'] = response['token_number']
            print(f"   Student created with ID: {response['id']}")
            print(f"   Token number: {response['token_number']}")
            return True
        return False

    def test_get_students(self, user_key):
        """Test getting students list"""
        success, response = self.run_test(
            f"Get students for {user_key}",
            "GET",
            "students",
            200,
            token_user=user_key
        )
        if success:
            print(f"   Found {len(response)} students")
        return success

    def test_file_upload(self, user_key):
        """Test document upload"""
        if 'student_id' not in self.test_data:
            print("❌ No student ID available for file upload test")
            return False
            
        # Create a temporary test PDF file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Write minimal PDF content
            f.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF')
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_tc.pdf', f, 'application/pdf')}
                data = {'document_type': 'tc'}
                
                success, response = self.run_test(
                    "Upload Document",
                    "POST",
                    f"students/{self.test_data['student_id']}/upload",
                    200,
                    data=data,
                    files=files,
                    token_user=user_key
                )
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
            
        return success

    def test_update_student_status(self, user_key, status):
        """Test updating student status"""
        if 'student_id' not in self.test_data:
            print("❌ No student ID available for status update test")
            return False
            
        # Use form data instead of JSON for this endpoint
        data = {
            'status': status,
            'notes': f'Test {status} by coordinator'
        }
        
        success, response = self.run_test(
            f"Update student status to {status}",
            "PUT",
            f"students/{self.test_data['student_id']}/status",
            200,
            data=data,
            files={},  # This will trigger form data mode
            token_user=user_key
        )
        return success

    def test_get_incentives(self, user_key):
        """Test getting incentives"""
        success, response = self.run_test(
            f"Get incentives for {user_key}",
            "GET",
            "incentives",
            200,
            token_user=user_key
        )
        if success:
            print(f"   Total earned: ₹{response.get('total_earned', 0)}")
            print(f"   Total pending: ₹{response.get('total_pending', 0)}")
            print(f"   Incentives count: {len(response.get('incentives', []))}")
        return success

    def test_admin_dashboard(self, user_key):
        """Test admin dashboard"""
        success, response = self.run_test(
            "Admin Dashboard",
            "GET",
            "admin/dashboard",
            200,
            token_user=user_key
        )
        if success:
            print(f"   Total admissions: {response.get('total_admissions', 0)}")
            print(f"   Active agents: {response.get('active_agents', 0)}")
            print(f"   Incentives paid: ₹{response.get('incentives_paid', 0)}")
            print(f"   Incentives unpaid: ₹{response.get('incentives_unpaid', 0)}")
        return success

    def test_get_incentive_rules(self):
        """Test getting incentive rules"""
        success, response = self.run_test(
            "Get Incentive Rules",
            "GET",
            "incentive-rules",
            200
        )
        if success:
            print(f"   Found {len(response)} incentive rules")
            for rule in response:
                print(f"   {rule.get('course')}: ₹{rule.get('amount')}")
        return success

def main():
    print("🚀 Starting Admission System API Tests")
    print("=" * 50)
    
    tester = AdmissionSystemAPITester()
    
    # Test credentials from the review request
    test_users = {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'coordinator': {'username': 'coordinator', 'password': 'coord123'},
        'agent1': {'username': 'agent1', 'password': 'agent123'},
        'agent2': {'username': 'agent2', 'password': 'agent123'}
    }
    
    print("\n📋 Phase 1: Authentication Tests")
    print("-" * 30)
    
    # Test login for all users
    login_success = True
    for user_key, credentials in test_users.items():
        if not tester.test_login(credentials['username'], credentials['password'], user_key):
            print(f"❌ Login failed for {user_key}, skipping related tests")
            login_success = False
    
    if not login_success:
        print("\n❌ Critical authentication failures detected")
        return 1
    
    # Test user info for all logged in users
    for user_key in tester.tokens.keys():
        tester.test_user_info(user_key)
    
    print("\n📋 Phase 2: Agent Workflow Tests")
    print("-" * 30)
    
    # Test agent workflow
    if 'agent1' in tester.tokens:
        tester.test_create_student('agent1')
        tester.test_get_students('agent1')
        tester.test_file_upload('agent1')
        tester.test_get_incentives('agent1')
    
    print("\n📋 Phase 3: Coordinator Workflow Tests")
    print("-" * 30)
    
    # Test coordinator workflow
    if 'coordinator' in tester.tokens:
        tester.test_get_students('coordinator')
        tester.test_update_student_status('coordinator', 'approved')
        
    print("\n📋 Phase 4: Admin Dashboard Tests")
    print("-" * 30)
    
    # Test admin functionality
    if 'admin' in tester.tokens:
        tester.test_admin_dashboard('admin')
        tester.test_get_students('admin')
        tester.test_get_incentives('admin')
    
    print("\n📋 Phase 5: General API Tests")
    print("-" * 30)
    
    # Test incentive rules (public endpoint)
    tester.test_get_incentive_rules()
    
    # Test incentives after approval (should have generated incentive)
    if 'agent1' in tester.tokens:
        tester.test_get_incentives('agent1')
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())