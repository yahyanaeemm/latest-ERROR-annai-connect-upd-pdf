#!/usr/bin/env python3
"""
Document Viewing Functionality Test
===================================

This test specifically addresses the coordinator document viewing issue where
coordinators see "No documents uploaded" when clicking the eye icon to view
student documents, even though agents can see document upload sections.

Focus Areas:
1. Document Upload Verification for "Fresh Start" student (AGI25080001)
2. Coordinator Document Retrieval API testing
3. Access Control Testing
4. Document Storage Investigation
5. Student Data Structure examination
"""

import requests
import sys
import json
from datetime import datetime
import os
import tempfile
from pathlib import Path
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

class DocumentViewingTester:
    def __init__(self, base_url="https://pdf-receipt-pro.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}
        self.tests_run = 0
        self.tests_passed = 0
        
        # Load environment variables for database access
        load_dotenv('backend/.env')
        self.mongo_url = os.environ['MONGO_URL']
        self.db_name = os.environ['DB_NAME']

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None, token_user=None):
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

    async def check_database_student_data(self):
        """Check the actual student data in the database"""
        print("\n🔍 DATABASE INVESTIGATION: Checking Fresh Start Student Data")
        print("-" * 60)
        
        client = AsyncIOMotorClient(self.mongo_url)
        db = client[self.db_name]
        
        try:
            # Find the Fresh Start student
            fresh_start_student = await db.students.find_one({
                '$or': [
                    {'first_name': 'Fresh', 'last_name': 'Start'},
                    {'token_number': 'AGI25080001'}
                ]
            })
            
            if not fresh_start_student:
                print("❌ Fresh Start student (AGI25080001) not found in database")
                return False
                
            print(f"✅ Found Fresh Start student in database:")
            print(f"   ID: {fresh_start_student.get('id')}")
            print(f"   Name: {fresh_start_student.get('first_name')} {fresh_start_student.get('last_name')}")
            print(f"   Token: {fresh_start_student.get('token_number')}")
            print(f"   Email: {fresh_start_student.get('email')}")
            print(f"   Status: {fresh_start_student.get('status')}")
            print(f"   Agent ID: {fresh_start_student.get('agent_id')}")
            
            # Check documents field
            documents = fresh_start_student.get('documents', {})
            print(f"   Documents field: {documents}")
            print(f"   Documents count: {len(documents)}")
            
            if documents:
                print("   Document details:")
                for doc_type, file_path in documents.items():
                    print(f"     - {doc_type}: {file_path}")
                    # Check if file exists
                    file_exists = Path(file_path).exists() if file_path else False
                    print(f"       File exists: {file_exists}")
            else:
                print("   ⚠️ No documents found in database for Fresh Start student")
                
            # Store student ID for API tests
            self.test_data['fresh_start_student_id'] = fresh_start_student.get('id')
            
            return True
            
        except Exception as e:
            print(f"❌ Database check failed: {str(e)}")
            return False
        finally:
            client.close()

    def check_uploads_directory(self):
        """Check the uploads directory structure"""
        print("\n📁 STORAGE INVESTIGATION: Checking Uploads Directory")
        print("-" * 55)
        
        uploads_dir = Path("/app/uploads")
        
        if not uploads_dir.exists():
            print("❌ Uploads directory does not exist")
            return False
            
        print(f"✅ Uploads directory exists: {uploads_dir}")
        
        # Check if Fresh Start student has a directory
        if 'fresh_start_student_id' in self.test_data:
            student_id = self.test_data['fresh_start_student_id']
            student_dir = uploads_dir / student_id
            
            print(f"   Checking student directory: {student_dir}")
            
            if student_dir.exists():
                print(f"✅ Student directory exists")
                files = list(student_dir.glob("*"))
                print(f"   Files in directory: {len(files)}")
                for file in files:
                    print(f"     - {file.name} ({file.stat().st_size} bytes)")
            else:
                print("⚠️ No directory found for Fresh Start student")
                print("   This explains why coordinators see 'No documents uploaded'")
        
        # List all student directories
        student_dirs = [d for d in uploads_dir.iterdir() if d.is_dir()]
        print(f"   Total student directories: {len(student_dirs)}")
        
        return True

    def test_upload_document_to_fresh_start(self):
        """Upload a test document to Fresh Start student to test the flow"""
        print("\n📤 DOCUMENT UPLOAD TEST: Adding Document to Fresh Start Student")
        print("-" * 65)
        
        if 'fresh_start_student_id' not in self.test_data:
            print("❌ Fresh Start student ID not available")
            return False
            
        student_id = self.test_data['fresh_start_student_id']
        
        # Create a test PDF document
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Write minimal PDF content
            f.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF')
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('fresh_start_tc.pdf', f, 'application/pdf')}
                data = {'document_type': 'tc'}
                
                # Try with agent token (agents should be able to upload)
                success, response = self.run_test(
                    "Upload Document to Fresh Start Student (as Agent)",
                    "POST",
                    f"students/{student_id}/upload",
                    200,
                    data=data,
                    files=files,
                    token_user='agent'
                )
                
                if success:
                    print("✅ Document uploaded successfully to Fresh Start student")
                    return True
                else:
                    print("❌ Failed to upload document to Fresh Start student")
                    return False
                    
        except Exception as e:
            print(f"❌ Document upload failed: {str(e)}")
            return False
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    def test_coordinator_document_access(self):
        """Test coordinator access to student documents"""
        print("\n👁️ COORDINATOR ACCESS TEST: Document Retrieval API")
        print("-" * 55)
        
        if 'fresh_start_student_id' not in self.test_data:
            print("❌ Fresh Start student ID not available")
            return False
            
        student_id = self.test_data['fresh_start_student_id']
        
        # Test coordinator access to documents endpoint
        success, response = self.run_test(
            "Coordinator Access to Fresh Start Documents",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user='coordinator'
        )
        
        if not success:
            print("❌ Coordinator cannot access documents endpoint")
            return False
            
        print("✅ Coordinator can access documents endpoint")
        
        # Analyze the response
        if 'documents' not in response:
            print("❌ Missing 'documents' field in response")
            return False
            
        documents = response['documents']
        print(f"   Documents returned: {len(documents)}")
        
        if len(documents) == 0:
            print("⚠️ No documents returned - this explains the 'No documents uploaded' issue")
            print("   Possible causes:")
            print("   1. Documents not actually uploaded to database")
            print("   2. File paths in database don't match actual files")
            print("   3. API not properly checking file existence")
        else:
            print("✅ Documents found in API response:")
            for doc in documents:
                print(f"     - Type: {doc.get('type')}")
                print(f"       Display Name: {doc.get('display_name')}")
                print(f"       File Name: {doc.get('file_name')}")
                print(f"       File Path: {doc.get('file_path')}")
                print(f"       Download URL: {doc.get('download_url')}")
                print(f"       File Exists: {doc.get('exists')}")
                
                # If file doesn't exist, that's the problem
                if not doc.get('exists'):
                    print(f"       ⚠️ File does not exist on filesystem!")
        
        return True

    def test_agent_document_access(self):
        """Test agent access to documents (should be denied)"""
        print("\n🚫 AGENT ACCESS TEST: Document Retrieval API")
        print("-" * 50)
        
        if 'fresh_start_student_id' not in self.test_data:
            print("❌ Fresh Start student ID not available")
            return False
            
        student_id = self.test_data['fresh_start_student_id']
        
        # Test agent access to documents endpoint (should fail with 403)
        success, response = self.run_test(
            "Agent Access to Fresh Start Documents (Should Fail)",
            "GET",
            f"students/{student_id}/documents",
            403,
            token_user='agent'
        )
        
        if success:
            print("✅ Agent properly denied access to documents endpoint")
            return True
        else:
            print("❌ Agent access control not working properly")
            return False

    def test_admin_document_access(self):
        """Test admin access to student documents"""
        print("\n👑 ADMIN ACCESS TEST: Document Retrieval API")
        print("-" * 50)
        
        if 'fresh_start_student_id' not in self.test_data:
            print("❌ Fresh Start student ID not available")
            return False
            
        student_id = self.test_data['fresh_start_student_id']
        
        # Test admin access to documents endpoint
        success, response = self.run_test(
            "Admin Access to Fresh Start Documents",
            "GET",
            f"students/{student_id}/documents",
            200,
            token_user='admin'
        )
        
        if not success:
            print("❌ Admin cannot access documents endpoint")
            return False
            
        print("✅ Admin can access documents endpoint")
        
        # Analyze the response (same as coordinator test)
        documents = response.get('documents', [])
        print(f"   Documents returned: {len(documents)}")
        
        if len(documents) == 0:
            print("⚠️ Admin also sees no documents - confirms the issue is not access control")
        else:
            print("✅ Admin can see documents:")
            for doc in documents:
                print(f"     - {doc.get('display_name')}: Exists={doc.get('exists')}")
        
        return True

    def test_document_endpoint_with_nonexistent_student(self):
        """Test documents endpoint with non-existent student"""
        print("\n🔍 EDGE CASE TEST: Non-existent Student Documents")
        print("-" * 55)
        
        fake_student_id = "fake-student-id-12345"
        
        success, response = self.run_test(
            "Documents for Non-existent Student (Should Return 404)",
            "GET",
            f"students/{fake_student_id}/documents",
            404,
            token_user='coordinator'
        )
        
        if success:
            print("✅ Non-existent student properly returns 404")
            return True
        else:
            print("❌ Non-existent student handling not working properly")
            return False

    async def run_comprehensive_document_test(self):
        """Run the complete document viewing test suite"""
        print("🔍 DOCUMENT VIEWING FUNCTIONALITY TEST")
        print("=" * 50)
        print("Testing coordinator document viewing issues")
        print("Focus: 'Fresh Start' student (AGI25080001)")
        print("=" * 50)
        
        # Step 1: Login as different users
        print("\n🔐 AUTHENTICATION SETUP")
        print("-" * 25)
        
        # Login as coordinator (main user experiencing the issue)
        if not self.test_login("arulanantham", "Arul@annaiconnect", "coordinator"):
            print("❌ Failed to login as coordinator")
            return False
            
        # Login as admin for comparison
        if not self.test_login("super admin", "Admin@annaiconnect", "admin"):
            print("❌ Failed to login as admin")
            return False
            
        # Login as agent for testing access control
        if not self.test_login("agent1", "agent@123", "agent"):
            print("❌ Failed to login as agent")
            return False
        
        # Step 2: Database investigation
        if not await self.check_database_student_data():
            print("❌ Database investigation failed")
            return False
        
        # Step 3: File system investigation
        if not self.check_uploads_directory():
            print("❌ File system investigation failed")
            return False
        
        # Step 4: Test document upload (to create test data if needed)
        if not self.test_upload_document_to_fresh_start():
            print("⚠️ Document upload test failed - continuing with existing data")
        
        # Step 5: Test coordinator document access (main issue)
        if not self.test_coordinator_document_access():
            print("❌ Coordinator document access test failed")
            return False
        
        # Step 6: Test access control
        if not self.test_agent_document_access():
            print("❌ Agent access control test failed")
            return False
            
        if not self.test_admin_document_access():
            print("❌ Admin document access test failed")
            return False
        
        # Step 7: Test edge cases
        if not self.test_document_endpoint_with_nonexistent_student():
            print("❌ Edge case test failed")
            return False
        
        # Step 8: Re-check database after upload
        print("\n🔍 POST-UPLOAD DATABASE CHECK")
        print("-" * 35)
        await self.check_database_student_data()
        
        # Step 9: Re-check file system after upload
        print("\n📁 POST-UPLOAD STORAGE CHECK")
        print("-" * 35)
        self.check_uploads_directory()
        
        # Step 10: Final coordinator test after upload
        print("\n👁️ FINAL COORDINATOR TEST (After Upload)")
        print("-" * 45)
        self.test_coordinator_document_access()
        
        return True

    def print_summary(self):
        """Print test summary and findings"""
        print("\n" + "=" * 60)
        print("📋 DOCUMENT VIEWING TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print("\n🔍 KEY FINDINGS:")
        print("-" * 15)
        
        if 'fresh_start_student_id' in self.test_data:
            print("✅ Fresh Start student (AGI25080001) found in database")
        else:
            print("❌ Fresh Start student not found")
            
        print("\n🎯 LIKELY ROOT CAUSE:")
        print("-" * 20)
        print("The 'No documents uploaded' issue is likely caused by:")
        print("1. Fresh Start student has empty documents field in database")
        print("2. No actual files uploaded to /app/uploads/{student_id}/ directory")
        print("3. API correctly returns empty documents array")
        print("4. Frontend shows 'No documents uploaded' message")
        
        print("\n💡 RECOMMENDED SOLUTION:")
        print("-" * 25)
        print("1. Verify document upload functionality is working")
        print("2. Check if agents can actually upload documents")
        print("3. Ensure uploaded files are properly stored in database")
        print("4. Verify file paths in database match actual file locations")
        print("5. Test complete upload → view workflow")

def main():
    """Main test execution"""
    tester = DocumentViewingTester()
    
    try:
        # Run the comprehensive test
        success = asyncio.run(tester.run_comprehensive_document_test())
        
        # Print summary
        tester.print_summary()
        
        if success:
            print("\n✅ Document viewing test completed successfully")
            return 0
        else:
            print("\n❌ Document viewing test failed")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())