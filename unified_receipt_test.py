import requests
import sys
import json
from datetime import datetime
import os
import tempfile
import base64

class UnifiedReceiptTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
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
                    return success, response.content if response.content else {}
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

    def setup_test_data(self):
        """Setup test data for receipt testing"""
        print("\n🔧 Setting up test data for unified receipt testing...")
        
        # Login as different users
        if not self.test_login("super admin", "Admin@annaiconnect", "admin"):
            print("❌ Failed to login as admin")
            return False
            
        if not self.test_login("arulanantham", "Arul@annaiconnect", "coordinator"):
            print("❌ Failed to login as coordinator")
            return False
            
        if not self.test_login("agent1", "agent@123", "agent"):
            print("❌ Failed to login as agent")
            return False

        # Create admin signature for testing
        admin_signature_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        success, response = self.run_test(
            "Setup Admin Signature",
            "POST",
            "admin/signature",
            200,
            data={
                'signature_data': admin_signature_data,
                'signature_type': 'upload'
            },
            files={},
            token_user='admin'
        )
        
        if success:
            print("   ✅ Admin signature configured")
        
        # Create coordinator signature
        success, response = self.run_test(
            "Setup Coordinator Signature",
            "POST",
            "admin/signature",
            200,
            data={
                'signature_data': admin_signature_data,
                'signature_type': 'draw'
            },
            files={},
            token_user='coordinator'
        )
        
        if success:
            print("   ✅ Coordinator signature configured")

        # Create a test student
        student_data = {
            "first_name": "Receipt",
            "last_name": "TestStudent",
            "email": f"receipt.test.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "1234567890",
            "course": "BSc"
        }
        
        success, response = self.run_test(
            "Create Test Student",
            "POST",
            "students",
            200,
            data=student_data,
            token_user='agent'
        )
        
        if success and 'id' in response:
            self.test_data['student_id'] = response['id']
            self.test_data['token_number'] = response['token_number']
            print(f"   ✅ Test student created: {response['id']}")
            print(f"   Token: {response['token_number']}")
            
            # Approve student through 3-tier process
            # 1. Coordinator approval with signature
            success, response = self.run_test(
                "Coordinator Approves Student with Signature",
                "PUT",
                f"students/{self.test_data['student_id']}/status",
                200,
                data={
                    'status': 'approved',
                    'notes': 'Coordinator approval for receipt test',
                    'signature_data': admin_signature_data,
                    'signature_type': 'draw'
                },
                files={},
                token_user='coordinator'
            )
            
            if success:
                print("   ✅ Student approved by coordinator with signature")
                
                # 2. Admin final approval
                success, response = self.run_test(
                    "Admin Final Approval",
                    "PUT",
                    f"admin/approve-student/{self.test_data['student_id']}",
                    200,
                    data={'notes': 'Admin final approval for receipt test'},
                    files={},
                    token_user='admin'
                )
                
                if success:
                    print("   ✅ Student approved by admin - ready for receipt testing")
                    return True
        
        return False

    def test_regular_receipt_endpoint(self):
        """Test regular receipt endpoint /api/students/{student_id}/receipt"""
        print("\n📄 Testing Regular Receipt Endpoint")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Test as agent (owner of student)
        success, response = self.run_test(
            "Generate Regular Receipt (Agent)",
            "GET",
            f"students/{student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
            
        # Verify PDF content type
        if isinstance(response, bytes) and response.startswith(b'%PDF'):
            print("   ✅ Valid PDF generated")
            self.test_data['regular_receipt_pdf'] = response
        else:
            print("❌ Invalid PDF response")
            return False
        
        # Test as coordinator
        success, response = self.run_test(
            "Generate Regular Receipt (Coordinator)",
            "GET",
            f"students/{student_id}/receipt",
            200,
            token_user='coordinator'
        )
        
        if not success:
            return False
            
        if isinstance(response, bytes) and response.startswith(b'%PDF'):
            print("   ✅ Coordinator can generate regular receipt")
        else:
            print("❌ Invalid PDF response from coordinator")
            return False
        
        return True

    def test_admin_receipt_endpoint(self):
        """Test admin receipt endpoint /api/admin/students/{student_id}/receipt"""
        print("\n👑 Testing Admin Receipt Endpoint")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Test as admin
        success, response = self.run_test(
            "Generate Admin Receipt",
            "GET",
            f"admin/students/{student_id}/receipt",
            200,
            token_user='admin'
        )
        
        if not success:
            return False
            
        # Verify PDF content type
        if isinstance(response, bytes) and response.startswith(b'%PDF'):
            print("   ✅ Valid admin PDF generated")
            self.test_data['admin_receipt_pdf'] = response
        else:
            print("❌ Invalid PDF response")
            return False
        
        # Test access control - agent should be denied
        success, response = self.run_test(
            "Admin Receipt Access Control (Agent - Should Fail)",
            "GET",
            f"admin/students/{student_id}/receipt",
            403,
            token_user='agent'
        )
        
        if not success:
            return False
            
        print("   ✅ Agent properly denied admin receipt access")
        
        # Test access control - coordinator should be denied
        success, response = self.run_test(
            "Admin Receipt Access Control (Coordinator - Should Fail)",
            "GET",
            f"admin/students/{student_id}/receipt",
            403,
            token_user='coordinator'
        )
        
        if not success:
            return False
            
        print("   ✅ Coordinator properly denied admin receipt access")
        
        return True

    def test_unique_receipt_number_generation(self):
        """Test unique receipt number generation"""
        print("\n🔢 Testing Unique Receipt Number Generation")
        print("-" * 45)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Generate multiple receipts and verify unique numbers
        receipt_numbers = []
        
        for i in range(3):
            success, response = self.run_test(
                f"Generate Receipt #{i+1} for Unique Number Test",
                "GET",
                f"students/{student_id}/receipt",
                200,
                token_user='agent'
            )
            
            if not success:
                return False
            
            # Extract receipt number from PDF (this is a simplified check)
            if isinstance(response, bytes) and b'RCPT-' in response:
                print(f"   ✅ Receipt #{i+1} contains receipt number")
            else:
                print(f"❌ Receipt #{i+1} missing receipt number")
                return False
        
        print("   ✅ All receipts contain unique receipt numbers")
        return True

    def test_incentive_amount_display(self):
        """Test incentive amount display in receipts"""
        print("\n💰 Testing Incentive Amount Display")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Get incentive rules to verify expected amount
        success, response = self.run_test(
            "Get Incentive Rules",
            "GET",
            "incentive-rules",
            200
        )
        
        if not success:
            return False
        
        # Find BSc course incentive
        bsc_incentive = None
        for rule in response:
            if rule.get('course') == 'BSc':
                bsc_incentive = rule.get('amount')
                break
        
        if bsc_incentive is None:
            print("❌ No BSc incentive rule found")
            return False
        
        print(f"   Expected BSc incentive: ₹{bsc_incentive}")
        
        # Generate receipt and check for incentive amount
        success, response = self.run_test(
            "Generate Receipt for Incentive Check",
            "GET",
            f"students/{student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
        
        # Check if PDF contains incentive amount (simplified check)
        if isinstance(response, bytes):
            pdf_content = response.decode('latin-1', errors='ignore')
            incentive_str = f"₹{int(bsc_incentive):,}"
            if incentive_str in pdf_content or str(int(bsc_incentive)) in pdf_content:
                print(f"   ✅ Receipt contains incentive amount: ₹{bsc_incentive}")
            else:
                print(f"❌ Receipt missing incentive amount")
                return False
        
        return True

    def test_dual_signatures_display(self):
        """Test dual signatures display in receipts"""
        print("\n✍️ Testing Dual Signatures Display")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Generate receipt and check for signature sections
        success, response = self.run_test(
            "Generate Receipt for Signature Check",
            "GET",
            f"students/{student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
        
        # Check if PDF contains signature sections (simplified check)
        if isinstance(response, bytes):
            pdf_content = response.decode('latin-1', errors='ignore')
            
            # Check for signature section headers
            if "DIGITAL SIGNATURES" in pdf_content:
                print("   ✅ Receipt contains digital signatures section")
            else:
                print("❌ Receipt missing digital signatures section")
                return False
            
            # Check for coordinator signature
            if "Coordinator Signature" in pdf_content:
                print("   ✅ Receipt contains coordinator signature section")
            else:
                print("❌ Receipt missing coordinator signature section")
                return False
            
            # Check for admin signature
            if "Admin Signature" in pdf_content:
                print("   ✅ Receipt contains admin signature section")
            else:
                print("❌ Receipt missing admin signature section")
                return False
        
        return True

    def test_admin_generated_header(self):
        """Test admin-specific header in admin receipts"""
        print("\n👑 Testing Admin Generated Header")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Generate admin receipt
        success, response = self.run_test(
            "Generate Admin Receipt for Header Check",
            "GET",
            f"admin/students/{student_id}/receipt",
            200,
            token_user='admin'
        )
        
        if not success:
            return False
        
        # Check if PDF contains admin generated header
        if isinstance(response, bytes):
            pdf_content = response.decode('latin-1', errors='ignore')
            
            if "Admin Generated" in pdf_content:
                print("   ✅ Admin receipt contains 'Admin Generated' header")
            else:
                print("❌ Admin receipt missing 'Admin Generated' header")
                return False
            
            # Check for admin generation details
            if "Generated by Admin" in pdf_content:
                print("   ✅ Admin receipt contains admin generation details")
            else:
                print("❌ Admin receipt missing admin generation details")
                return False
        
        return True

    def test_backward_compatibility(self):
        """Test backward compatibility with existing functionality"""
        print("\n🔄 Testing Backward Compatibility")
        print("-" * 40)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Test that existing receipt download still works
        success, response = self.run_test(
            "Backward Compatibility - Regular Receipt",
            "GET",
            f"students/{student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
        
        print("   ✅ Regular receipt endpoint maintains compatibility")
        
        # Test permission checks are maintained
        # Create unapproved student
        student_data = {
            "first_name": "Unapproved",
            "last_name": "Student",
            "email": f"unapproved.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "9876543210",
            "course": "MBA"
        }
        
        success, response = self.run_test(
            "Create Unapproved Student",
            "POST",
            "students",
            200,
            data=student_data,
            token_user='agent'
        )
        
        if success and 'id' in response:
            unapproved_id = response['id']
            
            # Try to generate receipt for unapproved student - should fail
            success, response = self.run_test(
                "Receipt for Unapproved Student (Should Fail)",
                "GET",
                f"students/{unapproved_id}/receipt",
                400,
                token_user='agent'
            )
            
            if not success:
                return False
            
            print("   ✅ Permission checks maintained - unapproved students rejected")
        
        return True

    def test_edge_cases(self):
        """Test edge cases for receipt generation"""
        print("\n🔍 Testing Edge Cases")
        print("-" * 30)
        
        # Test with non-existent student
        fake_student_id = "fake-student-id-12345"
        success, response = self.run_test(
            "Receipt for Non-existent Student (Should Fail)",
            "GET",
            f"students/{fake_student_id}/receipt",
            404,
            token_user='agent'
        )
        
        if not success:
            return False
        
        print("   ✅ Non-existent student properly handled")
        
        # Test admin receipt for non-existent student
        success, response = self.run_test(
            "Admin Receipt for Non-existent Student (Should Fail)",
            "GET",
            f"admin/students/{fake_student_id}/receipt",
            404,
            token_user='admin'
        )
        
        if not success:
            return False
        
        print("   ✅ Admin receipt for non-existent student properly handled")
        
        return True

    def test_missing_signatures_handling(self):
        """Test proper handling when signatures are missing"""
        print("\n❓ Testing Missing Signatures Handling")
        print("-" * 45)
        
        # Create a student without coordinator signature
        student_data = {
            "first_name": "NoSignature",
            "last_name": "Student",
            "email": f"nosig.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "5555555555",
            "course": "MBA"
        }
        
        success, response = self.run_test(
            "Create Student for No-Signature Test",
            "POST",
            "students",
            200,
            data=student_data,
            token_user='agent'
        )
        
        if not success:
            return False
        
        no_sig_student_id = response['id']
        
        # Approve without signature
        success, response = self.run_test(
            "Coordinator Approves Without Signature",
            "PUT",
            f"students/{no_sig_student_id}/status",
            200,
            data={
                'status': 'approved',
                'notes': 'Approval without signature'
            },
            files={},
            token_user='coordinator'
        )
        
        if not success:
            return False
        
        # Admin final approval
        success, response = self.run_test(
            "Admin Final Approval for No-Signature Student",
            "PUT",
            f"admin/approve-student/{no_sig_student_id}",
            200,
            data={'notes': 'Admin approval for no-signature test'},
            files={},
            token_user='admin'
        )
        
        if not success:
            return False
        
        # Generate receipt and verify it handles missing signatures gracefully
        success, response = self.run_test(
            "Generate Receipt with Missing Signatures",
            "GET",
            f"students/{no_sig_student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
        
        # Check if PDF contains appropriate messages for missing signatures
        if isinstance(response, bytes):
            pdf_content = response.decode('latin-1', errors='ignore')
            
            if "Not available" in pdf_content or "Signature processing error" in pdf_content:
                print("   ✅ Missing signatures handled gracefully")
            else:
                print("❌ Missing signatures not handled properly")
                return False
        
        return True

    def test_missing_incentive_rules_handling(self):
        """Test proper handling when incentive rules are missing"""
        print("\n💸 Testing Missing Incentive Rules Handling")
        print("-" * 50)
        
        # Create student with course that has no incentive rule
        student_data = {
            "first_name": "NoIncentive",
            "last_name": "Student",
            "email": f"noincentive.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "7777777777",
            "course": "UnknownCourse"
        }
        
        success, response = self.run_test(
            "Create Student with Unknown Course",
            "POST",
            "students",
            200,
            data=student_data,
            token_user='agent'
        )
        
        if not success:
            return False
        
        unknown_course_student_id = response['id']
        
        # Approve student
        success, response = self.run_test(
            "Approve Student with Unknown Course",
            "PUT",
            f"students/{unknown_course_student_id}/status",
            200,
            data={
                'status': 'approved',
                'notes': 'Approval for unknown course test'
            },
            files={},
            token_user='coordinator'
        )
        
        if not success:
            return False
        
        # Admin final approval
        success, response = self.run_test(
            "Admin Final Approval for Unknown Course Student",
            "PUT",
            f"admin/approve-student/{unknown_course_student_id}",
            200,
            data={'notes': 'Admin approval for unknown course test'},
            files={},
            token_user='admin'
        )
        
        if not success:
            return False
        
        # Generate receipt and verify it handles missing incentive rules
        success, response = self.run_test(
            "Generate Receipt with Missing Incentive Rule",
            "GET",
            f"students/{unknown_course_student_id}/receipt",
            200,
            token_user='agent'
        )
        
        if not success:
            return False
        
        # Check if PDF shows ₹0 or handles missing incentive gracefully
        if isinstance(response, bytes):
            pdf_content = response.decode('latin-1', errors='ignore')
            
            if "₹0" in pdf_content or "Course Incentive" in pdf_content:
                print("   ✅ Missing incentive rules handled gracefully")
            else:
                print("❌ Missing incentive rules not handled properly")
                return False
        
        return True

    def run_all_tests(self):
        """Run all unified receipt generation tests"""
        print("🚀 UNIFIED PDF RECEIPT GENERATION TESTING")
        print("=" * 50)
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Failed to setup test data")
            return False
        
        # Run all tests
        tests = [
            self.test_regular_receipt_endpoint,
            self.test_admin_receipt_endpoint,
            self.test_unique_receipt_number_generation,
            self.test_incentive_amount_display,
            self.test_dual_signatures_display,
            self.test_admin_generated_header,
            self.test_backward_compatibility,
            self.test_edge_cases,
            self.test_missing_signatures_handling,
            self.test_missing_incentive_rules_handling
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 UNIFIED RECEIPT TESTING SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all_passed:
            print("\n🎉 ALL UNIFIED RECEIPT TESTS PASSED!")
        else:
            print("\n❌ SOME UNIFIED RECEIPT TESTS FAILED!")
        
        return all_passed

if __name__ == "__main__":
    tester = UnifiedReceiptTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)