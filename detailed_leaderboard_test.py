#!/usr/bin/env python3
"""
Detailed Leaderboard System Test
More comprehensive test to verify leaderboard structure and data integrity.
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class DetailedLeaderboardTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None

    def login_admin(self):
        """Login as admin user"""
        print("🔐 Logging in as admin...")
        
        success, response = self.run_api_test(
            "Admin Login",
            "POST",
            "login",
            200,
            data={"username": "super admin", "password": "Admin@annaiconnect"}
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"✅ Admin login successful - Role: {response.get('role')}")
            return True
        else:
            print(f"❌ Admin login failed - {response}")
            return False

    def run_api_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                try:
                    error_detail = response.json()
                    return False, {"error": error_detail, "status": response.status_code}
                except:
                    return False, {"error": response.text, "status": response.status_code}

        except Exception as e:
            return False, {"error": str(e)}

    def check_system_data(self):
        """Check what data exists in the system"""
        print("\n🔍 Checking System Data...")
        
        # Check users
        success, response = self.run_api_test("Get User Info", "GET", "me", 200)
        if success:
            print(f"   Current user: {response.get('username')} ({response.get('role')})")
        
        # Check students
        success, response = self.run_api_test("Get Students", "GET", "students", 200)
        if success:
            students = response if isinstance(response, list) else []
            print(f"   Total students: {len(students)}")
            if students:
                approved_count = sum(1 for s in students if s.get('status') == 'approved')
                print(f"   Approved students: {approved_count}")
        
        # Check incentives
        success, response = self.run_api_test("Get Incentives", "GET", "incentives", 200)
        if success:
            incentives = response.get('incentives', []) if isinstance(response, dict) else []
            print(f"   Total incentives: {len(incentives)}")
            total_amount = sum(i.get('amount', 0) for i in incentives)
            print(f"   Total incentive amount: ₹{total_amount}")
        
        # Check admin dashboard
        success, response = self.run_api_test("Admin Dashboard", "GET", "admin/dashboard", 200)
        if success:
            print(f"   Dashboard - Total admissions: {response.get('total_admissions', 0)}")
            print(f"   Dashboard - Active agents: {response.get('active_agents', 0)}")

    def test_leaderboard_structure(self):
        """Test leaderboard response structure in detail"""
        print("\n📊 Testing Leaderboard Response Structure...")
        
        # Test overall leaderboard
        success, response = self.run_api_test("Overall Leaderboard", "GET", "leaderboard/overall", 200)
        if success:
            print(f"   Overall leaderboard response keys: {list(response.keys())}")
            
            # Check if it's the new format with leaderboard key
            if 'leaderboard' in response:
                leaderboard = response['leaderboard']
                print(f"   Leaderboard agents: {len(leaderboard)}")
                print(f"   Total agents: {response.get('total_agents', 'N/A')}")
                print(f"   Type: {response.get('type', 'N/A')}")
                
                if leaderboard:
                    first_agent = leaderboard[0]
                    print(f"   First agent structure: {list(first_agent.keys())}")
                    print(f"   First agent: {first_agent.get('full_name')} - {first_agent.get('total_admissions')} admissions")
            else:
                # Old format - direct list
                agents = response if isinstance(response, list) else []
                print(f"   Direct list format - {len(agents)} agents")
                if agents:
                    first_agent = agents[0]
                    print(f"   First agent structure: {list(first_agent.keys())}")

    def test_all_leaderboard_endpoints(self):
        """Test all leaderboard endpoints"""
        print("\n🎯 Testing All Leaderboard Endpoints...")
        
        endpoints = [
            ("Overall", "leaderboard/overall"),
            ("Weekly", "leaderboard/weekly"),
            ("Monthly", "leaderboard/monthly"),
            ("Date Range", "leaderboard/date-range?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59")
        ]
        
        for name, endpoint in endpoints:
            success, response = self.run_api_test(f"{name} Leaderboard", "GET", endpoint, 200)
            if success:
                # Handle both old and new response formats
                if 'leaderboard' in response:
                    agents = response['leaderboard']
                    total_agents = response.get('total_agents', len(agents))
                    leaderboard_type = response.get('type', name.lower())
                    print(f"   {name}: {len(agents)} agents (total: {total_agents}, type: {leaderboard_type})")
                else:
                    agents = response if isinstance(response, list) else []
                    print(f"   {name}: {len(agents)} agents (direct list format)")
                
                # Check agent structure if any exist
                if agents:
                    agent = agents[0]
                    required_fields = ['agent_id', 'username', 'full_name', 'total_admissions', 'total_incentive', 'rank', 'is_top_3']
                    missing_fields = [field for field in required_fields if field not in agent]
                    if missing_fields:
                        print(f"     ⚠️ Missing fields: {missing_fields}")
                    else:
                        print(f"     ✅ All required fields present")
            else:
                print(f"   ❌ {name} failed: {response.get('error')}")

    def run_detailed_tests(self):
        """Run all detailed tests"""
        print("🚀 Starting Detailed Leaderboard System Tests")
        print("=" * 60)
        
        if not self.login_admin():
            return False
        
        self.check_system_data()
        self.test_leaderboard_structure()
        self.test_all_leaderboard_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ DETAILED LEADERBOARD TESTS COMPLETED")
        print("=" * 60)
        
        return True

def main():
    """Main function"""
    tester = DetailedLeaderboardTester()
    success = tester.run_detailed_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()