import requests
import sys
import json
from datetime import datetime
import os
import tempfile
import base64

class DetailedReceiptTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}
        self.test_data = {}

    def test_login(self, username, password, user_key):
        """Test login and store token"""
        response = requests.post(f"{self.api_url}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            self.tokens[user_key] = data['access_token']
            print(f"✅ Logged in as {username}")
            return True
        print(f"❌ Failed to login as {username}")
        return False

    def setup_test_environment(self):
        """Setup complete test environment"""
        print("🔧 Setting up detailed test environment...")
        
        # Login as admin
        if not self.test_login("super admin", "Admin@annaiconnect", "admin"):
            return False
        
        # Check existing incentive rules
        headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/incentive-rules", headers=headers)
        
        if response.status_code == 200:
            rules = response.json()
            print(f"📋 Found {len(rules)} existing incentive rules:")
            for rule in rules:
                print(f"   - {rule['course']}: ₹{rule['amount']}")
        
        # Create BSc incentive rule if it doesn't exist
        bsc_exists = any(rule['course'] == 'BSc' for rule in rules)
        if not bsc_exists:
            print("📝 Creating BSc incentive rule...")
            response = requests.post(
                f"{self.api_url}/admin/courses",
                data={'course': 'BSc', 'amount': '6000'},
                headers={'Authorization': f'Bearer {self.tokens["admin"]}'}
            )
            if response.status_code == 200:
                print("   ✅ BSc incentive rule created: ₹6000")
            else:
                print(f"   ❌ Failed to create BSc rule: {response.status_code}")
        
        # Login as other users
        if not self.test_login("arulanantham", "Arul@annaiconnect", "coordinator"):
            return False
        if not self.test_login("agent1", "agent@123", "agent"):
            return False
        
        return True

    def create_and_approve_student(self):
        """Create and fully approve a student for testing"""
        print("👨‍🎓 Creating and approving test student...")
        
        # Create student
        student_data = {
            "first_name": "Detailed",
            "last_name": "TestStudent",
            "email": f"detailed.test.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "1234567890",
            "course": "BSc"
        }
        
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.post(f"{self.api_url}/students", json=student_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to create student: {response.status_code}")
            return False
        
        student = response.json()
        self.test_data['student_id'] = student['id']
        self.test_data['token_number'] = student['token_number']
        print(f"   ✅ Student created: {student['id']}")
        print(f"   Token: {student['token_number']}")
        
        # Setup signatures
        signature_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Admin signature
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        requests.post(
            f"{self.api_url}/admin/signature",
            data={'signature_data': signature_data, 'signature_type': 'upload'},
            headers=admin_headers
        )
        
        # Coordinator signature
        coord_headers = {'Authorization': f'Bearer {self.tokens["coordinator"]}'}
        requests.post(
            f"{self.api_url}/admin/signature",
            data={'signature_data': signature_data, 'signature_type': 'draw'},
            headers=coord_headers
        )
        
        # Coordinator approval with signature
        response = requests.put(
            f"{self.api_url}/students/{student['id']}/status",
            data={
                'status': 'approved',
                'notes': 'Coordinator approval with signature',
                'signature_data': signature_data,
                'signature_type': 'draw'
            },
            headers=coord_headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed coordinator approval: {response.status_code}")
            return False
        
        print("   ✅ Coordinator approved with signature")
        
        # Admin final approval
        response = requests.put(
            f"{self.api_url}/admin/approve-student/{student['id']}",
            data={'notes': 'Admin final approval'},
            headers=admin_headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed admin approval: {response.status_code}")
            return False
        
        print("   ✅ Admin final approval completed")
        return True

    def test_receipt_content_detailed(self):
        """Test receipt content in detail"""
        print("\n📄 Testing Receipt Content in Detail")
        print("-" * 45)
        
        if 'student_id' not in self.test_data:
            print("❌ No test student available")
            return False
        
        student_id = self.test_data['student_id']
        
        # Test regular receipt
        headers = {'Authorization': f'Bearer {self.tokens["agent"]}'}
        response = requests.get(f"{self.api_url}/students/{student_id}/receipt", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to generate regular receipt: {response.status_code}")
            return False
        
        # Save PDF for analysis
        with open('/tmp/regular_receipt.pdf', 'wb') as f:
            f.write(response.content)
        
        print("   ✅ Regular receipt generated and saved")
        
        # Test admin receipt
        admin_headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
        response = requests.get(f"{self.api_url}/admin/students/{student_id}/receipt", headers=admin_headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to generate admin receipt: {response.status_code}")
            return False
        
        # Save PDF for analysis
        with open('/tmp/admin_receipt.pdf', 'wb') as f:
            f.write(response.content)
        
        print("   ✅ Admin receipt generated and saved")
        
        # Analyze PDF content using pdfplumber if available, otherwise basic analysis
        try:
            import pdfplumber
            
            # Analyze regular receipt
            print("\n📊 Regular Receipt Analysis:")
            with pdfplumber.open('/tmp/regular_receipt.pdf') as pdf:
                text = pdf.pages[0].extract_text()
                print("   Content found:")
                
                # Check for key elements
                checks = [
                    ("AnnaiCONNECT", "Institution header"),
                    ("Student Admission Receipt", "Receipt title"),
                    ("ADMISSION CONFIRMED", "Confirmation text"),
                    ("STUDENT DETAILS", "Student section"),
                    ("PROCESS DETAILS", "Process section"),
                    ("DIGITAL SIGNATURES", "Signature section"),
                    ("Token Number:", "Token field"),
                    ("Course Incentive:", "Incentive field"),
                    ("Receipt ID:", "Receipt ID"),
                    (self.test_data['token_number'], "Actual token number"),
                    ("BSc", "Course name"),
                    ("₹6,000", "Incentive amount"),
                    ("Coordinator Signature:", "Coordinator signature label"),
                    ("Admin Signature:", "Admin signature label")
                ]
                
                for check_text, description in checks:
                    if check_text in text:
                        print(f"   ✅ {description}: Found")
                    else:
                        print(f"   ❌ {description}: Missing")
            
            # Analyze admin receipt
            print("\n📊 Admin Receipt Analysis:")
            with pdfplumber.open('/tmp/admin_receipt.pdf') as pdf:
                text = pdf.pages[0].extract_text()
                
                admin_checks = [
                    ("Admin Generated", "Admin generated header"),
                    ("Generated by Admin:", "Admin generation details"),
                    ("super admin", "Admin username")
                ]
                
                for check_text, description in admin_checks:
                    if check_text in text:
                        print(f"   ✅ {description}: Found")
                    else:
                        print(f"   ❌ {description}: Missing")
        
        except ImportError:
            print("   ⚠️ pdfplumber not available, using basic PDF analysis")
            
            # Basic binary analysis
            with open('/tmp/regular_receipt.pdf', 'rb') as f:
                content = f.read()
                
            # Convert to string for basic text search (not ideal but works for basic checks)
            try:
                text_content = content.decode('latin-1', errors='ignore')
                
                basic_checks = [
                    ("AnnaiCONNECT", "Institution header"),
                    ("DIGITAL SIGNATURES", "Signature section"),
                    ("Receipt ID", "Receipt ID"),
                    ("Course Incentive", "Incentive field"),
                    (self.test_data['token_number'], "Token number")
                ]
                
                for check_text, description in basic_checks:
                    if check_text in text_content:
                        print(f"   ✅ {description}: Found")
                    else:
                        print(f"   ❌ {description}: Missing")
                        
            except Exception as e:
                print(f"   ⚠️ Could not analyze PDF content: {e}")
        
        return True

    def run_detailed_tests(self):
        """Run all detailed tests"""
        print("🚀 DETAILED UNIFIED RECEIPT TESTING")
        print("=" * 50)
        
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        if not self.create_and_approve_student():
            print("❌ Failed to create and approve student")
            return False
        
        if not self.test_receipt_content_detailed():
            print("❌ Failed detailed receipt content test")
            return False
        
        print("\n🎉 DETAILED TESTING COMPLETED!")
        return True

if __name__ == "__main__":
    tester = DetailedReceiptTester()
    success = tester.run_detailed_tests()
    sys.exit(0 if success else 1)