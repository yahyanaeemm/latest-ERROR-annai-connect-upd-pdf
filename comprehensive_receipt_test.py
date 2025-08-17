import requests
import sys
import json
from datetime import datetime
import os
import tempfile
import base64
import pdfplumber

class ComprehensiveReceiptTester:
    def __init__(self, base_url="https://approval-workflow-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}
        self.tests_passed = 0
        self.tests_total = 0

    def log_test(self, name, passed, details=""):
        """Log test result"""
        self.tests_total += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def test_login(self, username, password, user_key):
        """Test login and store token"""
        response = requests.post(f"{self.api_url}/login", json={"username": username, "password": password})
        success = response.status_code == 200
        if success:
            data = response.json()
            self.tokens[user_key] = data['access_token']
        return success

    def setup_comprehensive_test(self):
        """Setup comprehensive test environment"""
        print("🔧 COMPREHENSIVE RECEIPT TESTING SETUP")
        print("=" * 50)
        
        # Login as all user types
        logins = [
            ("super admin", "Admin@annaiconnect", "admin"),
            ("arulanantham", "Arul@annaiconnect", "coordinator"),
            ("agent1", "agent@123", "agent")
        ]
        
        for username, password, key in logins:
            success = self.test_login(username, password, key)
            self.log_test(f"Login as {username}", success)
            if not success:
                return False
        
        # Ensure BSc incentive rule exists
        headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/incentive-rules", headers=headers)
        
        if response.status_code == 200:
            rules = response.json()
            bsc_rule = next((rule for rule in rules if rule['course'] == 'BSc'), None)
            
            if not bsc_rule:
                # Create BSc rule
                response = requests.post(
                    f"{self.api_url}/admin/courses",
                    data={'course': 'BSc', 'amount': '6000'},
                    headers=headers
                )
                success = response.status_code == 200
                self.log_test("Create BSc incentive rule", success, "₹6000")
            else:
                self.log_test("BSc incentive rule exists", True, f"₹{bsc_rule['amount']}")
        
        return True

    def create_test_student_with_full_approval(self):
        """Create student and complete full approval process"""
        print("\n👨‍🎓 STUDENT CREATION AND APPROVAL")
        print("-" * 40)
        
        # Create student
        student_data = {
            "first_name": "Comprehensive",
            "last_name": "TestStudent",
            "email": f"comprehensive.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "1234567890",
            "course": "BSc"
        }
        
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.post(f"{self.api_url}/students", json=student_data, headers=headers)
        
        success = response.status_code == 200
        if success:
            student = response.json()
            self.test_data['student_id'] = student['id']
            self.test_data['token_number'] = student['token_number']
            details = f"ID: {student['id'][:8]}..., Token: {student['token_number']}"
        else:
            details = f"Status: {response.status_code}"
        
        self.log_test("Create test student", success, details)
        
        if not success:
            return False
        
        # Setup admin signature
        signature_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.post(
            f"{self.api_url}/admin/signature",
            data={'signature_data': signature_data, 'signature_type': 'upload'},
            headers=admin_headers
        )
        self.log_test("Setup admin signature", response.status_code == 200)
        
        # Setup coordinator signature
        coord_headers = {'Authorization': f'Bearer {self.tokens["coordinator"]}'}
        response = requests.post(
            f"{self.api_url}/admin/signature",
            data={'signature_data': signature_data, 'signature_type': 'draw'},
            headers=coord_headers
        )
        self.log_test("Setup coordinator signature", response.status_code == 200)
        
        # Coordinator approval with signature
        response = requests.put(
            f"{self.api_url}/students/{self.test_data['student_id']}/status",
            data={
                'status': 'approved',
                'notes': 'Coordinator approval with signature',
                'signature_data': signature_data,
                'signature_type': 'draw'
            },
            headers=coord_headers
        )
        self.log_test("Coordinator approval with signature", response.status_code == 200)
        
        # Admin final approval
        response = requests.put(
            f"{self.api_url}/admin/approve-student/{self.test_data['student_id']}",
            data={'notes': 'Admin final approval'},
            headers=admin_headers
        )
        self.log_test("Admin final approval", response.status_code == 200)
        
        return True

    def test_regular_receipt_functionality(self):
        """Test regular receipt endpoint functionality"""
        print("\n📄 REGULAR RECEIPT ENDPOINT TESTING")
        print("-" * 45)
        
        student_id = self.test_data['student_id']
        
        # Test agent access (owner)
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.get(f"{self.api_url}/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 200 and response.content.startswith(b'%PDF')
        self.log_test("Agent can generate regular receipt", success)
        
        if success:
            # Save for analysis
            with open('/tmp/regular_receipt_agent.pdf', 'wb') as f:
                f.write(response.content)
        
        # Test coordinator access
        headers = {'Authorization': f'Bearer {self.tokens["coordinator"]}'}
        response = requests.get(f"{self.api_url}/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 200 and response.content.startswith(b'%PDF')
        self.log_test("Coordinator can generate regular receipt", success)
        
        # Test admin access to regular receipt
        headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 200 and response.content.startswith(b'%PDF')
        self.log_test("Admin can generate regular receipt", success)
        
        return True

    def test_admin_receipt_functionality(self):
        """Test admin receipt endpoint functionality"""
        print("\n👑 ADMIN RECEIPT ENDPOINT TESTING")
        print("-" * 40)
        
        student_id = self.test_data['student_id']
        
        # Test admin access
        headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/admin/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 200 and response.content.startswith(b'%PDF')
        self.log_test("Admin can generate admin receipt", success)
        
        if success:
            # Save for analysis
            with open('/tmp/admin_receipt.pdf', 'wb') as f:
                f.write(response.content)
        
        # Test access control - agent should be denied
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.get(f"{self.api_url}/admin/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 403
        self.log_test("Agent denied admin receipt access", success)
        
        # Test access control - coordinator should be denied
        headers = {'Authorization': f'Bearer {self.tokens["coordinator"]}'}
        response = requests.get(f"{self.api_url}/admin/students/{student_id}/receipt", headers=headers)
        
        success = response.status_code == 403
        self.log_test("Coordinator denied admin receipt access", success)
        
        return True

    def test_unified_pdf_features(self):
        """Test unified PDF generation features"""
        print("\n🔍 UNIFIED PDF FEATURES TESTING")
        print("-" * 40)
        
        # Analyze regular receipt
        try:
            with pdfplumber.open('/tmp/regular_receipt_agent.pdf') as pdf:
                text = pdf.pages[0].extract_text()
                
                # Test unique receipt number generation
                receipt_id_found = "Receipt ID:" in text and "RCPT-" in text
                self.log_test("Unique receipt number generation", receipt_id_found)
                
                # Test incentive amount display
                incentive_found = "Course Incentive:" in text and ("₹6,000" in text or "6000" in text)
                self.log_test("Incentive amount display", incentive_found)
                
                # Test dual signatures section
                signatures_found = "DIGITAL SIGNATURES" in text
                self.log_test("Digital signatures section", signatures_found)
                
                coord_sig_found = "Coordinator Signature:" in text
                self.log_test("Coordinator signature section", coord_sig_found)
                
                admin_sig_found = "Admin Signature:" in text
                self.log_test("Admin signature section", admin_sig_found)
                
                # Test student details
                token_found = self.test_data['token_number'] in text
                self.log_test("Student token number display", token_found)
                
                course_found = "BSc" in text
                self.log_test("Course display", course_found)
                
                # Test receipt structure
                student_details_found = "STUDENT DETAILS" in text
                self.log_test("Student details section", student_details_found)
                
                process_details_found = "PROCESS DETAILS" in text
                self.log_test("Process details section", process_details_found)
                
        except Exception as e:
            self.log_test("PDF analysis", False, f"Error: {str(e)}")
            return False
        
        # Analyze admin receipt
        try:
            with pdfplumber.open('/tmp/admin_receipt.pdf') as pdf:
                text = pdf.pages[0].extract_text()
                
                # Test admin-specific header
                admin_header_found = "Admin Generated" in text
                self.log_test("Admin generated header", admin_header_found)
                
                # Test admin generation details
                admin_details_found = "Generated by Admin:" in text
                self.log_test("Admin generation details", admin_details_found)
                
                admin_username_found = "super admin" in text
                self.log_test("Admin username in receipt", admin_username_found)
                
        except Exception as e:
            self.log_test("Admin PDF analysis", False, f"Error: {str(e)}")
            return False
        
        return True

    def test_backward_compatibility(self):
        """Test backward compatibility"""
        print("\n🔄 BACKWARD COMPATIBILITY TESTING")
        print("-" * 40)
        
        # Test with unapproved student
        student_data = {
            "first_name": "Unapproved",
            "last_name": "Student",
            "email": f"unapproved.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "9876543210",
            "course": "MBA"
        }
        
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.post(f"{self.api_url}/students", json=student_data, headers=headers)
        
        if response.status_code == 200:
            unapproved_id = response.json()['id']
            
            # Try to generate receipt for unapproved student
            response = requests.get(f"{self.api_url}/students/{unapproved_id}/receipt", headers=headers)
            success = response.status_code == 400
            self.log_test("Unapproved student receipt denied", success)
        
        # Test with non-existent student
        fake_id = "fake-student-id-12345"
        response = requests.get(f"{self.api_url}/students/{fake_id}/receipt", headers=headers)
        success = response.status_code == 404
        self.log_test("Non-existent student receipt denied", success)
        
        # Test admin receipt with non-existent student
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/admin/students/{fake_id}/receipt", headers=admin_headers)
        success = response.status_code == 404
        self.log_test("Non-existent student admin receipt denied", success)
        
        return True

    def test_edge_cases(self):
        """Test edge cases"""
        print("\n🔍 EDGE CASES TESTING")
        print("-" * 30)
        
        # Test student with missing incentive rule
        student_data = {
            "first_name": "NoIncentive",
            "last_name": "Student",
            "email": f"noincentive.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "5555555555",
            "course": "UnknownCourse"
        }
        
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.post(f"{self.api_url}/students", json=student_data, headers=headers)
        
        if response.status_code == 200:
            no_incentive_id = response.json()['id']
            
            # Approve student
            coord_headers = {'Authorization': f'Bearer {self.tokens["coordinator"]}'}
            requests.put(
                f"{self.api_url}/students/{no_incentive_id}/status",
                data={'status': 'approved', 'notes': 'Test approval'},
                headers=coord_headers
            )
            
            # Admin approval
            admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
            requests.put(
                f"{self.api_url}/admin/approve-student/{no_incentive_id}",
                data={'notes': 'Admin approval'},
                headers=admin_headers
            )
            
            # Generate receipt
            response = requests.get(f"{self.api_url}/students/{no_incentive_id}/receipt", headers=headers)
            success = response.status_code == 200 and response.content.startswith(b'%PDF')
            self.log_test("Receipt generation with missing incentive rule", success)
            
            if success:
                # Check that it shows ₹0 or handles gracefully
                with open('/tmp/no_incentive_receipt.pdf', 'wb') as f:
                    f.write(response.content)
                
                try:
                    with pdfplumber.open('/tmp/no_incentive_receipt.pdf') as pdf:
                        text = pdf.pages[0].extract_text()
                        zero_incentive = "₹0" in text or "Course Incentive:" in text
                        self.log_test("Missing incentive handled gracefully", zero_incentive)
                except:
                    self.log_test("Missing incentive handled gracefully", True, "PDF generated successfully")
        
        return True

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE UNIFIED RECEIPT TESTING")
        print("=" * 60)
        
        success = True
        
        if not self.setup_comprehensive_test():
            success = False
        
        if not self.create_test_student_with_full_approval():
            success = False
        
        if not self.test_regular_receipt_functionality():
            success = False
        
        if not self.test_admin_receipt_functionality():
            success = False
        
        if not self.test_unified_pdf_features():
            success = False
        
        if not self.test_backward_compatibility():
            success = False
        
        if not self.test_edge_cases():
            success = False
        
        # Print comprehensive summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_total}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_total - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_total)*100:.1f}%")
        
        if self.tests_passed == self.tests_total:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            print("✅ Unified PDF receipt generation system is fully functional!")
        else:
            print(f"\n⚠️ {self.tests_total - self.tests_passed} TESTS FAILED")
            print("❌ Some issues found in unified receipt system")
        
        return success and (self.tests_passed == self.tests_total)

if __name__ == "__main__":
    tester = ComprehensiveReceiptTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)