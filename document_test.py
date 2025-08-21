import requests
import sys
import json
from datetime import datetime
import os
import tempfile
from pathlib import Path

class DocumentAPITester:
    def __init__(self, base_url="https://admissions-hub-4.preview.emergentagent.com"):
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
                    return success, response
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

    def create_test_files(self):
        """Create test files for upload testing"""
        test_files = {}
        
        # Create a test PDF file
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF'
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            f.write(pdf_content)
            test_files['pdf'] = f.name
        
        # Create a test JPG file (minimal JPEG header)
        jpg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
            f.write(jpg_content)
            test_files['jpg'] = f.name
        
        # Create a test PNG file (minimal PNG header)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            f.write(png_content)
            test_files['png'] = f.name
        
        return test_files

    def cleanup_test_files(self, test_files):
        """Clean up temporary test files"""
        for file_path in test_files.values():
            try:
                os.unlink(file_path)
            except:
                pass

    def test_document_upload_various_types(self, user_key, student_id):
        """Test document upload with various file types"""
        print(f"\n📄 Testing Document Upload - Various File Types")
        print("-" * 50)
        
        test_files = self.create_test_files()
        upload_results = {}
        
        try:
            # Test PDF upload
            with open(test_files['pdf'], 'rb') as f:
                files = {'file': ('test_tc.pdf', f, 'application/pdf')}
                data = {'document_type': 'tc'}
                
                success, response = self.run_test(
                    "Upload PDF Document (TC)",
                    "POST",
                    f"students/{student_id}/upload",
                    200,
                    data=data,
                    files=files,
                    token_user=user_key
                )
                upload_results['pdf'] = success
                if success:
                    print(f"   ✅ PDF upload successful: {response.get('message', 'No message')}")
            
            # Test JPG upload
            with open(test_files['jpg'], 'rb') as f:
                files = {'file': ('test_photo.jpg', f, 'image/jpeg')}
                data = {'document_type': 'photo'}
                
                success, response = self.run_test(
                    "Upload JPG Document (Photo)",
                    "POST",
                    f"students/{student_id}/upload",
                    200,
                    data=data,
                    files=files,
                    token_user=user_key
                )
                upload_results['jpg'] = success
                if success:
                    print(f"   ✅ JPG upload successful: {response.get('message', 'No message')}")
            
            # Test PNG upload
            with open(test_files['png'], 'rb') as f:
                files = {'file': ('test_certificate.png', f, 'image/png')}
                data = {'document_type': 'certificate'}
                
                success, response = self.run_test(
                    "Upload PNG Document (Certificate)",
                    "POST",
                    f"students/{student_id}/upload",
                    200,
                    data=data,
                    files=files,
                    token_user=user_key
                )
                upload_results['png'] = success
                if success:
                    print(f"   ✅ PNG upload successful: {response.get('message', 'No message')}")
            
            # Test invalid file type (should fail)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("This is a text file")
                txt_file = f.name
            
            try:
                with open(txt_file, 'rb') as f:
                    files = {'file': ('test_invalid.txt', f, 'text/plain')}
                    data = {'document_type': 'invalid'}
                    
                    success, response = self.run_test(
                        "Upload Invalid File Type (Should Fail)",
                        "POST",
                        f"students/{student_id}/upload",
                        400,
                        data=data,
                        files=files,
                        token_user=user_key
                    )
                    upload_results['invalid'] = success
                    if success:
                        print(f"   ✅ Invalid file type properly rejected")
            finally:
                os.unlink(txt_file)
            
        finally:
            self.cleanup_test_files(test_files)
        
        return all(upload_results.values())

    def test_document_retrieval(self, user_key, student_id):
        """Test document retrieval API"""
        print(f"\n📋 Testing Document Retrieval API")
        print("-" * 35)
        
        success, response = self.run_test(
            "Get Student Documents",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user=user_key
        )
        
        if not success:
            return False
        
        # Verify response structure
        if 'student_id' not in response:
            print("❌ Missing student_id in response")
            return False
        
        if 'documents' not in response:
            print("❌ Missing documents array in response")
            return False
        
        documents = response['documents']
        print(f"   ✅ Found {len(documents)} documents")
        
        # Verify document structure
        for doc in documents:
            required_fields = ['type', 'display_name', 'file_name', 'file_path', 'download_url', 'exists']
            for field in required_fields:
                if field not in doc:
                    print(f"❌ Missing field '{field}' in document info")
                    return False
            
            # Verify download URL format
            if not doc['download_url'].startswith('/api/students/'):
                print(f"❌ Invalid download URL format: {doc['download_url']}")
                return False
            
            print(f"   ✅ Document: {doc['display_name']} - {doc['file_name']} (exists: {doc['exists']})")
        
        # Store document info for download tests
        self.test_data['documents'] = documents
        
        return True

    def test_document_download_new_api(self, user_key, student_id):
        """Test the new document download API endpoint"""
        print(f"\n⬇️ Testing NEW Document Download API")
        print("-" * 40)
        
        if 'documents' not in self.test_data:
            print("❌ No documents available for download test")
            return False
        
        documents = self.test_data['documents']
        download_results = []
        
        for doc in documents:
            if not doc['exists']:
                print(f"   ⚠️ Skipping {doc['type']} - file doesn't exist")
                continue
            
            success, response = self.run_test(
                f"Download {doc['display_name']} ({doc['type']})",
                "GET",
                f"students/{student_id}/documents/{doc['type']}/download",
                200,
                token_user=user_key
            )
            
            if success:
                # Check if it's a streaming response
                if hasattr(response, 'headers'):
                    content_type = response.headers.get('content-type', '')
                    content_disposition = response.headers.get('content-disposition', '')
                    
                    print(f"   ✅ Download successful")
                    print(f"      Content-Type: {content_type}")
                    print(f"      Content-Disposition: {content_disposition}")
                    
                    # Verify proper content type
                    if doc['file_name'].endswith('.pdf') and 'application/pdf' not in content_type:
                        print(f"   ⚠️ Expected PDF content type, got: {content_type}")
                    elif doc['file_name'].endswith(('.jpg', '.jpeg')) and 'image/jpeg' not in content_type:
                        print(f"   ⚠️ Expected JPEG content type, got: {content_type}")
                    elif doc['file_name'].endswith('.png') and 'image/png' not in content_type:
                        print(f"   ⚠️ Expected PNG content type, got: {content_type}")
                    
                    # Verify attachment header
                    if 'attachment' not in content_disposition:
                        print(f"   ⚠️ Missing attachment header in Content-Disposition")
                else:
                    print(f"   ✅ Download successful (response type: {type(response)})")
            
            download_results.append(success)
        
        return all(download_results) if download_results else True

    def test_document_access_control(self, student_id):
        """Test document access control - agents should be denied"""
        print(f"\n🔒 Testing Document Access Control")
        print("-" * 35)
        
        access_control_results = []
        
        # Test agent access to document retrieval (should fail)
        if 'agent' in self.tokens:
            success, response = self.run_test(
                "Agent Access to Document Retrieval (Should Fail)",
                "GET",
                f"students/{student_id}/documents",
                403,
                token_user='agent'
            )
            access_control_results.append(success)
            if success:
                print("   ✅ Agent properly denied document retrieval access")
        
        # Test agent access to document download (should fail)
        if 'agent' in self.tokens and 'documents' in self.test_data:
            documents = self.test_data['documents']
            if documents:
                doc = documents[0]  # Test with first document
                success, response = self.run_test(
                    "Agent Access to Document Download (Should Fail)",
                    "GET",
                    f"students/{student_id}/documents/{doc['type']}/download",
                    403,
                    token_user='agent'
                )
                access_control_results.append(success)
                if success:
                    print("   ✅ Agent properly denied document download access")
        
        # Test coordinator access (should succeed)
        if 'coordinator' in self.tokens:
            success, response = self.run_test(
                "Coordinator Access to Document Retrieval (Should Succeed)",
                "GET",
                f"students/{student_id}/documents",
                200,
                token_user='coordinator'
            )
            access_control_results.append(success)
            if success:
                print("   ✅ Coordinator properly allowed document retrieval access")
        
        # Test admin access (should succeed)
        if 'admin' in self.tokens:
            success, response = self.run_test(
                "Admin Access to Document Retrieval (Should Succeed)",
                "GET",
                f"students/{student_id}/documents",
                200,
                token_user='admin'
            )
            access_control_results.append(success)
            if success:
                print("   ✅ Admin properly allowed document retrieval access")
        
        return all(access_control_results)

    def test_document_error_handling(self, user_key):
        """Test document API error handling"""
        print(f"\n⚠️ Testing Document API Error Handling")
        print("-" * 40)
        
        error_handling_results = []
        
        # Test with non-existent student
        fake_student_id = "fake-student-id-12345"
        success, response = self.run_test(
            "Document Retrieval for Non-existent Student (Should Fail)",
            "GET",
            f"students/{fake_student_id}/documents",
            404,
            token_user=user_key
        )
        error_handling_results.append(success)
        if success:
            print("   ✅ Non-existent student properly handled")
        
        # Test download for non-existent document type
        if 'documents' in self.test_data and self.test_data['documents']:
            student_id = self.test_data['documents'][0].get('student_id', 'test-student')
            success, response = self.run_test(
                "Download Non-existent Document Type (Should Fail)",
                "GET",
                f"students/{student_id}/documents/nonexistent/download",
                404,
                token_user=user_key
            )
            error_handling_results.append(success)
            if success:
                print("   ✅ Non-existent document type properly handled")
        
        return all(error_handling_results)

    def test_existing_functionality_regression(self, user_key):
        """Test that existing functionality still works"""
        print(f"\n🔄 Testing Existing Functionality Regression")
        print("-" * 45)
        
        regression_results = []
        
        # Test basic student listing
        success, response = self.run_test(
            "Get Students List (Regression Test)",
            "GET",
            "students",
            200,
            token_user=user_key
        )
        regression_results.append(success)
        if success:
            print(f"   ✅ Students list working - found {len(response)} students")
        
        # Test incentive rules
        success, response = self.run_test(
            "Get Incentive Rules (Regression Test)",
            "GET",
            "incentive-rules",
            200
        )
        regression_results.append(success)
        if success:
            print(f"   ✅ Incentive rules working - found {len(response)} rules")
        
        # Test user info
        success, response = self.run_test(
            "Get User Info (Regression Test)",
            "GET",
            "me",
            200,
            token_user=user_key
        )
        regression_results.append(success)
        if success:
            print(f"   ✅ User info working - {response.get('username')} ({response.get('role')})")
        
        return all(regression_results)

    def run_comprehensive_document_tests(self):
        """Run all document-related tests"""
        print("🚀 Starting Comprehensive Document API Testing")
        print("=" * 60)
        
        # Login with different user types
        print("\n🔐 Authentication Phase")
        print("-" * 25)
        
        login_success = True
        
        # Login as coordinator
        if not self.test_login("arulanantham", "Arul@annaiconnect", "coordinator"):
            print("❌ Failed to login as coordinator")
            login_success = False
        
        # Login as agent
        if not self.test_login("agent1", "agent@123", "agent"):
            print("❌ Failed to login as agent")
            login_success = False
        
        # Login as admin (try different admin credentials)
        admin_login_success = False
        admin_credentials = [
            ("super admin", "Admin@annaiconnect"),
            ("admin", "admin@123"),
            ("superadmin", "admin@123")
        ]
        
        for username, password in admin_credentials:
            if self.test_login(username, password, "admin"):
                admin_login_success = True
                break
        
        if not admin_login_success:
            print("❌ Failed to login as admin with any credentials")
            login_success = False
        
        if not login_success:
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Use the specified student ID from the review request
        student_id = "cac25fc9-a0a1-4991-9e55-bb676df1f2ae"  # Fresh Start student
        
        # Test document upload (as agent - agents can upload)
        print(f"\n📤 Document Upload Testing Phase")
        print("-" * 35)
        upload_success = self.test_document_upload_various_types("agent", student_id)
        
        # Test document retrieval (as coordinator)
        print(f"\n📋 Document Retrieval Testing Phase")
        print("-" * 40)
        retrieval_success = self.test_document_retrieval("coordinator", student_id)
        
        # Test new document download API (as coordinator)
        print(f"\n⬇️ Document Download Testing Phase")
        print("-" * 35)
        download_success = self.test_document_download_new_api("coordinator", student_id)
        
        # Test access control
        print(f"\n🔒 Access Control Testing Phase")
        print("-" * 30)
        access_control_success = self.test_document_access_control(student_id)
        
        # Test error handling
        print(f"\n⚠️ Error Handling Testing Phase")
        print("-" * 30)
        error_handling_success = self.test_document_error_handling("coordinator")
        
        # Test existing functionality regression
        print(f"\n🔄 Regression Testing Phase")
        print("-" * 25)
        regression_success = self.test_existing_functionality_regression("coordinator")
        
        # Summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 20)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        all_phases_success = all([
            upload_success,
            retrieval_success, 
            download_success,
            access_control_success,
            error_handling_success,
            regression_success
        ])
        
        if all_phases_success:
            print("\n🎉 ALL DOCUMENT TESTS PASSED!")
            print("✅ Document upload API working correctly")
            print("✅ Document retrieval API working correctly") 
            print("✅ NEW document download API working correctly")
            print("✅ Access control working correctly")
            print("✅ Error handling working correctly")
            print("✅ No regression in existing functionality")
        else:
            print("\n❌ SOME DOCUMENT TESTS FAILED!")
            print(f"Upload Success: {'✅' if upload_success else '❌'}")
            print(f"Retrieval Success: {'✅' if retrieval_success else '❌'}")
            print(f"Download Success: {'✅' if download_success else '❌'}")
            print(f"Access Control Success: {'✅' if access_control_success else '❌'}")
            print(f"Error Handling Success: {'✅' if error_handling_success else '❌'}")
            print(f"Regression Success: {'✅' if regression_success else '❌'}")
        
        return all_phases_success

if __name__ == "__main__":
    tester = DocumentAPITester()
    success = tester.run_comprehensive_document_tests()
    sys.exit(0 if success else 1)