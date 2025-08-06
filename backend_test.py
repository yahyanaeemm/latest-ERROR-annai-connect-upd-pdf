import requests
import sys
import json
from datetime import datetime
import os
import tempfile

class AdmissionSystemAPITester:
    def __init__(self, base_url="https://ca50f5d0-c6b1-47c4-887c-3b2ab848852a.preview.emergentagent.com"):
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
                if files is not None:  # Check for None specifically, not just falsy
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

    # NEW ENHANCED FEATURES TESTS
    
    def test_signature_status_update(self, user_key, status):
        """Test updating student status with signature data"""
        if 'student_id' not in self.test_data:
            print("❌ No student ID available for signature status update test")
            return False
            
        # Mock base64 signature data
        signature_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        data = {
            'status': status,
            'notes': f'Test {status} with signature',
            'signature_data': signature_data,
            'signature_type': 'draw'
        }
        
        success, response = self.run_test(
            f"Update student status to {status} with signature",
            "PUT",
            f"students/{self.test_data['student_id']}/status",
            200,
            data=data,
            files={},  # This will trigger form data mode
            token_user=user_key
        )
        return success

    def test_course_management_apis(self, user_key):
        """Test course management CRUD operations"""
        course_name = f"Test Course {datetime.now().strftime('%H%M%S')}"
        course_amount = 5000.0
        
        # Test create course - using form data as expected by the API
        create_data = {
            'course': course_name,
            'amount': course_amount  # Keep as float, requests will handle conversion
        }
        
        success, response = self.run_test(
            "Create Course Rule",
            "POST",
            "admin/courses",
            200,
            data=create_data,
            files={},  # This triggers form data mode
            token_user=user_key
        )
        
        if not success:
            return False
            
        course_id = response.get('id')
        if course_id:
            self.test_data['course_id'] = course_id
            print(f"   Course created with ID: {course_id}")
        
        # Test update course - using form data
        update_data = {
            'course': f"{course_name} Updated",
            'amount': 6000.0  # Keep as float, requests will handle conversion
        }
        
        success, response = self.run_test(
            "Update Course Rule",
            "PUT",
            f"admin/courses/{course_id}",
            200,
            data=update_data,
            files={},  # This triggers form data mode
            token_user=user_key
        )
        
        if not success:
            return False
        
        # Test delete course (soft delete)
        success, response = self.run_test(
            "Delete Course Rule",
            "DELETE",
            f"admin/courses/{course_id}",
            200,
            token_user=user_key
        )
        
        return success

    def test_pdf_receipt_generation(self, user_key):
        """Test PDF receipt generation"""
        if 'student_id' not in self.test_data:
            print("❌ No student ID available for PDF receipt test")
            return False
            
        success, response = self.run_test(
            "Generate PDF Receipt",
            "GET",
            f"students/{self.test_data['student_id']}/receipt",
            200,
            token_user=user_key
        )
        
        if success:
            print("   PDF receipt generated successfully")
        return success

    def test_filtered_excel_export(self, user_key):
        """Test enhanced Excel export with filters"""
        # Test with various filter combinations
        filter_tests = [
            # Test with no filters
            {},
            # Test with date filters
            {
                'start_date': '2024-01-01T00:00:00',
                'end_date': '2024-12-31T23:59:59'
            },
            # Test with status filter - CRITICAL: Test "all" value fix
            {
                'status': 'all'
            },
            # Test with other status values
            {
                'status': 'approved'
            },
            {
                'status': 'pending'
            },
            {
                'status': 'rejected'
            },
            # Test with course filter
            {
                'course': 'BSc'
            }
        ]
        
        all_passed = True
        for i, filters in enumerate(filter_tests):
            query_params = '&'.join([f"{k}={v}" for k, v in filters.items()])
            endpoint = f"admin/export/excel?{query_params}" if query_params else "admin/export/excel"
            
            success, response = self.run_test(
                f"Excel Export Test {i+1} ({len(filters)} filters)",
                "GET",
                endpoint,
                200,
                token_user=user_key
            )
            
            if not success:
                all_passed = False
        
        return all_passed

    def test_admin_incentive_management(self, user_key):
        """Test admin incentive management APIs"""
        # First get all incentives
        success, response = self.run_test(
            "Get All Incentives (Admin)",
            "GET",
            "admin/incentives",
            200,
            token_user=user_key
        )
        
        if not success:
            return False
            
        incentives = response if isinstance(response, list) else []
        print(f"   Found {len(incentives)} incentives")
        
        # Test updating incentive status if we have incentives
        if incentives:
            incentive_id = incentives[0].get('id')
            if incentive_id:
                # Test marking as paid
                paid_data = {'status': 'paid'}
                success, response = self.run_test(
                    "Mark Incentive as Paid",
                    "PUT",
                    f"admin/incentives/{incentive_id}/status",
                    200,
                    data=paid_data,
                    files={},
                    token_user=user_key
                )
                
                if not success:
                    return False
                
                # Test marking as unpaid
                unpaid_data = {'status': 'unpaid'}
                success, response = self.run_test(
                    "Mark Incentive as Unpaid",
                    "PUT",
                    f"admin/incentives/{incentive_id}/status",
                    200,
                    data=unpaid_data,
                    files={},
                    token_user=user_key
                )
                
                return success
        
        print("   No incentives found to test status updates")
        return True

    def test_create_student_with_new_course(self, user_key, course_name):
        """Test creating a student with a specific course"""
        student_data = {
            "first_name": "Enhanced",
            "last_name": "Student",
            "email": f"enhanced.student.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "9876543210",
            "course": course_name
        }
        
        success, response = self.run_test(
            f"Create Student with {course_name}",
            "POST",
            "students",
            200,
            data=student_data,
            token_user=user_key
        )
        
        if success and 'id' in response:
            self.test_data['enhanced_student_id'] = response['id']
            print(f"   Enhanced student created with ID: {response['id']}")
            return True
        return False

    def test_comprehensive_workflow(self):
        """Test complete workflow with new features"""
        print("\n🔄 Testing Complete Enhanced Workflow")
        print("-" * 40)
        
        workflow_success = True
        
        # 1. Admin creates a new course
        if 'admin' in self.tokens:
            if not self.test_course_management_apis('admin'):
                workflow_success = False
        
        # 2. Agent creates student with new course
        if 'agent1' in self.tokens:
            if not self.test_create_student_with_new_course('agent1', 'MBA'):
                workflow_success = False
        
        # 3. Coordinator approves with signature
        if 'coordinator' in self.tokens and 'enhanced_student_id' in self.test_data:
            # Update test_data to use enhanced student for signature test
            original_student_id = self.test_data.get('student_id')
            self.test_data['student_id'] = self.test_data['enhanced_student_id']
            
            if not self.test_signature_status_update('coordinator', 'approved'):
                workflow_success = False
                
            # Restore original student_id
            if original_student_id:
                self.test_data['student_id'] = original_student_id
        
        # 4. Agent downloads PDF receipt
        if 'agent1' in self.tokens:
            if not self.test_pdf_receipt_generation('agent1'):
                workflow_success = False
        
        # 5. Admin manages incentives
        if 'admin' in self.tokens:
            if not self.test_admin_incentive_management('admin'):
                workflow_success = False
        
        # 6. Admin exports filtered data
        if 'admin' in self.tokens:
            if not self.test_filtered_excel_export('admin'):
                workflow_success = False
        
        return workflow_success

def main():
    print("🚀 Starting Enhanced Admission System API Tests")
    print("=" * 60)
    
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
    
    print("\n📋 Phase 2: Basic Agent Workflow Tests")
    print("-" * 30)
    
    # Test basic agent workflow
    if 'agent1' in tester.tokens:
        tester.test_create_student('agent1')
        tester.test_get_students('agent1')
        tester.test_file_upload('agent1')
        tester.test_get_incentives('agent1')
    
    print("\n📋 Phase 3: Enhanced E-Signature Tests (HIGH PRIORITY)")
    print("-" * 30)
    
    # Test enhanced coordinator workflow with signature
    if 'coordinator' in tester.tokens:
        tester.test_get_students('coordinator')
        tester.test_signature_status_update('coordinator', 'approved')
        
    print("\n📋 Phase 4: Course Management Tests (HIGH PRIORITY)")
    print("-" * 30)
    
    # Test course management APIs
    if 'admin' in tester.tokens:
        tester.test_course_management_apis('admin')
        
    print("\n📋 Phase 5: PDF Receipt Generation Tests (HIGH PRIORITY)")
    print("-" * 30)
    
    # Test PDF receipt generation
    if 'agent1' in tester.tokens:
        tester.test_pdf_receipt_generation('agent1')
    
    print("\n📋 Phase 6: Enhanced Export Tests (MEDIUM PRIORITY)")
    print("-" * 30)
    
    # Test filtered Excel export
    if 'admin' in tester.tokens:
        tester.test_filtered_excel_export('admin')
    
    print("\n📋 Phase 7: Incentive Management Tests (MEDIUM PRIORITY)")
    print("-" * 30)
    
    # Test admin incentive management
    if 'admin' in tester.tokens:
        tester.test_admin_incentive_management('admin')
    
    print("\n📋 Phase 8: Admin Dashboard Tests")
    print("-" * 30)
    
    # Test admin functionality
    if 'admin' in tester.tokens:
        tester.test_admin_dashboard('admin')
        tester.test_get_students('admin')
        tester.test_get_incentives('admin')
    
    print("\n📋 Phase 9: General API Tests")
    print("-" * 30)
    
    # Test incentive rules (public endpoint)
    tester.test_get_incentive_rules()
    
    # Test incentives after approval (should have generated incentive)
    if 'agent1' in tester.tokens:
        tester.test_get_incentives('agent1')
    
    print("\n📋 Phase 10: Comprehensive Workflow Test")
    print("-" * 30)
    
    # Test complete enhanced workflow
    tester.test_comprehensive_workflow()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All enhanced tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())