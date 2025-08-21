#!/usr/bin/env python3
"""
Leaderboard System Verification Test
Quick sanity check to ensure leaderboard APIs are working correctly after incentive masking feature implementation.
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import os

class LeaderboardVerificationTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        self.test_results.append(result)
        print(result)

    def run_api_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add authorization if admin token available
        if self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            
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

    def login_admin(self):
        """Login as admin user"""
        print("🔐 Logging in as admin...")
        
        # Try different admin credentials
        admin_credentials = [
            {"username": "super admin", "password": "admin123"},
            {"username": "admin", "password": "admin123"},
            {"username": "superadmin", "password": "admin123"}
        ]
        
        for creds in admin_credentials:
            success, response = self.run_api_test(
                f"Admin Login ({creds['username']})",
                "POST",
                "login",
                200,
                data=creds
            )
            
            if success and 'access_token' in response:
                self.admin_token = response['access_token']
                self.log_result(f"Admin Login ({creds['username']})", True, f"Role: {response.get('role')}")
                return True
            else:
                self.log_result(f"Admin Login ({creds['username']})", False, f"Status: {response.get('status', 'Unknown')}")
        
        return False

    def test_leaderboard_overall(self):
        """Test overall leaderboard endpoint"""
        print("\n📊 Testing Overall Leaderboard...")
        
        success, response = self.run_api_test(
            "Overall Leaderboard",
            "GET",
            "leaderboard/overall",
            200
        )
        
        if success:
            agents = response if isinstance(response, list) else []
            details = f"Found {len(agents)} agents"
            
            # Verify response structure
            if agents:
                first_agent = agents[0]
                required_fields = ['agent_id', 'username', 'full_name', 'total_admissions', 'total_incentive', 'rank', 'is_top_3']
                missing_fields = [field for field in required_fields if field not in first_agent]
                
                if missing_fields:
                    details += f" | Missing fields: {missing_fields}"
                    success = False
                else:
                    details += f" | Top agent: {first_agent.get('full_name', first_agent.get('username'))} ({first_agent.get('total_admissions')} admissions, ₹{first_agent.get('total_incentive', 0)})"
            
            self.log_result("Overall Leaderboard", success, details)
        else:
            self.log_result("Overall Leaderboard", False, f"Error: {response.get('error')}")
        
        return success

    def test_leaderboard_weekly(self):
        """Test weekly leaderboard endpoint"""
        print("\n📅 Testing Weekly Leaderboard...")
        
        success, response = self.run_api_test(
            "Weekly Leaderboard",
            "GET",
            "leaderboard/weekly",
            200
        )
        
        if success:
            agents = response if isinstance(response, list) else []
            details = f"Found {len(agents)} agents"
            
            # Verify response structure and weekly calculation
            if agents:
                first_agent = agents[0]
                required_fields = ['agent_id', 'username', 'full_name', 'total_admissions', 'total_incentive', 'rank', 'is_top_3']
                missing_fields = [field for field in required_fields if field not in first_agent]
                
                if missing_fields:
                    details += f" | Missing fields: {missing_fields}"
                    success = False
                else:
                    details += f" | Top weekly: {first_agent.get('full_name', first_agent.get('username'))} ({first_agent.get('total_admissions')} admissions)"
            
            self.log_result("Weekly Leaderboard", success, details)
        else:
            self.log_result("Weekly Leaderboard", False, f"Error: {response.get('error')}")
        
        return success

    def test_leaderboard_monthly(self):
        """Test monthly leaderboard endpoint"""
        print("\n📆 Testing Monthly Leaderboard...")
        
        success, response = self.run_api_test(
            "Monthly Leaderboard",
            "GET",
            "leaderboard/monthly",
            200
        )
        
        if success:
            agents = response if isinstance(response, list) else []
            details = f"Found {len(agents)} agents"
            
            # Verify response structure and badge assignment
            if agents:
                first_agent = agents[0]
                required_fields = ['agent_id', 'username', 'full_name', 'total_admissions', 'total_incentive', 'rank', 'is_top_3']
                missing_fields = [field for field in required_fields if field not in first_agent]
                
                if missing_fields:
                    details += f" | Missing fields: {missing_fields}"
                    success = False
                else:
                    # Check for top 3 badge assignment
                    top_3_count = sum(1 for agent in agents[:3] if agent.get('is_top_3'))
                    details += f" | Top monthly: {first_agent.get('full_name', first_agent.get('username'))} | Top 3 badges: {top_3_count}/3"
            
            self.log_result("Monthly Leaderboard", success, details)
        else:
            self.log_result("Monthly Leaderboard", False, f"Error: {response.get('error')}")
        
        return success

    def test_leaderboard_date_range(self):
        """Test custom date range leaderboard endpoint"""
        print("\n📊 Testing Custom Date Range Leaderboard...")
        
        # Test with 30-day range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        success, response = self.run_api_test(
            "Date Range Leaderboard",
            "GET",
            f"leaderboard/date-range?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
            200
        )
        
        if success:
            agents = response if isinstance(response, list) else []
            details = f"Found {len(agents)} agents for 30-day range"
            
            # Verify response structure
            if agents:
                first_agent = agents[0]
                required_fields = ['agent_id', 'username', 'full_name', 'total_admissions', 'total_incentive', 'rank', 'is_top_3']
                missing_fields = [field for field in required_fields if field not in first_agent]
                
                if missing_fields:
                    details += f" | Missing fields: {missing_fields}"
                    success = False
                else:
                    details += f" | Top in range: {first_agent.get('full_name', first_agent.get('username'))} ({first_agent.get('total_admissions')} admissions)"
            
            self.log_result("Date Range Leaderboard", success, details)
        else:
            self.log_result("Date Range Leaderboard", False, f"Error: {response.get('error')}")
        
        return success

    def test_data_consistency(self):
        """Test data consistency across different leaderboard endpoints"""
        print("\n🔍 Testing Data Consistency...")
        
        # Get all leaderboard data
        overall_success, overall_data = self.run_api_test("Overall Data", "GET", "leaderboard/overall", 200)
        weekly_success, weekly_data = self.run_api_test("Weekly Data", "GET", "leaderboard/weekly", 200)
        monthly_success, monthly_data = self.run_api_test("Monthly Data", "GET", "leaderboard/monthly", 200)
        
        if not (overall_success and weekly_success and monthly_success):
            self.log_result("Data Consistency", False, "Failed to fetch all leaderboard data")
            return False
        
        # Check that all endpoints return agent data
        overall_agents = overall_data if isinstance(overall_data, list) else []
        weekly_agents = weekly_data if isinstance(weekly_data, list) else []
        monthly_agents = monthly_data if isinstance(monthly_data, list) else []
        
        # Verify agent IDs are consistent
        overall_agent_ids = set(agent.get('agent_id') for agent in overall_agents)
        weekly_agent_ids = set(agent.get('agent_id') for agent in weekly_agents)
        monthly_agent_ids = set(agent.get('agent_id') for agent in monthly_agents)
        
        # All endpoints should have the same agents (though with different metrics)
        if overall_agent_ids == weekly_agent_ids == monthly_agent_ids:
            details = f"Consistent agent IDs across all endpoints ({len(overall_agent_ids)} agents)"
            success = True
        else:
            details = f"Inconsistent agent IDs: Overall={len(overall_agent_ids)}, Weekly={len(weekly_agent_ids)}, Monthly={len(monthly_agent_ids)}"
            success = False
        
        # Check ranking consistency (rank 1 should be highest admissions)
        for endpoint_name, agents in [("Overall", overall_agents), ("Weekly", weekly_agents), ("Monthly", monthly_agents)]:
            if agents:
                sorted_by_admissions = sorted(agents, key=lambda x: x.get('total_admissions', 0), reverse=True)
                if agents != sorted_by_admissions:
                    details += f" | {endpoint_name} ranking incorrect"
                    success = False
        
        self.log_result("Data Consistency", success, details)
        return success

    def test_backend_data_structure(self):
        """Verify backend data structure remains unchanged"""
        print("\n🏗️ Testing Backend Data Structure...")
        
        success, response = self.run_api_test(
            "Overall Leaderboard Structure",
            "GET",
            "leaderboard/overall",
            200
        )
        
        if success:
            agents = response if isinstance(response, list) else []
            
            if not agents:
                self.log_result("Backend Data Structure", True, "No agents found - structure valid for empty state")
                return True
            
            # Check first agent structure
            first_agent = agents[0]
            expected_structure = {
                'agent_id': str,
                'username': str,
                'full_name': str,
                'total_admissions': (int, float),
                'total_incentive': (int, float),
                'rank': int,
                'is_top_3': bool
            }
            
            structure_valid = True
            missing_fields = []
            wrong_types = []
            
            for field, expected_type in expected_structure.items():
                if field not in first_agent:
                    missing_fields.append(field)
                    structure_valid = False
                elif not isinstance(first_agent[field], expected_type):
                    wrong_types.append(f"{field}: expected {expected_type}, got {type(first_agent[field])}")
                    structure_valid = False
            
            if structure_valid:
                details = f"Structure valid for {len(agents)} agents"
            else:
                details = f"Structure issues - Missing: {missing_fields}, Wrong types: {wrong_types}"
            
            self.log_result("Backend Data Structure", structure_valid, details)
            return structure_valid
        else:
            self.log_result("Backend Data Structure", False, f"Error: {response.get('error')}")
            return False

    def run_verification_tests(self):
        """Run all leaderboard verification tests"""
        print("🚀 Starting Leaderboard System Verification Tests")
        print("=" * 60)
        
        # Login as admin (optional for leaderboard endpoints)
        admin_login_success = self.login_admin()
        if not admin_login_success:
            print("⚠️ Admin login failed - continuing with public endpoints")
        
        # Run all leaderboard tests
        test_results = []
        
        test_results.append(self.test_leaderboard_overall())
        test_results.append(self.test_leaderboard_weekly())
        test_results.append(self.test_leaderboard_monthly())
        test_results.append(self.test_leaderboard_date_range())
        test_results.append(self.test_data_consistency())
        test_results.append(self.test_backend_data_structure())
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 LEADERBOARD VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed ({(self.tests_passed/self.tests_run)*100:.1f}%)")
        
        if all(test_results):
            print("🎉 ALL LEADERBOARD TESTS PASSED - System is working correctly!")
            return True
        else:
            print("⚠️ Some leaderboard tests failed - Review results above")
            return False

def main():
    """Main function to run leaderboard verification"""
    tester = LeaderboardVerificationTester()
    success = tester.run_verification_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()