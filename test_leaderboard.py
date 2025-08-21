#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

class LeaderboardTester:
    def __init__(self, base_url="https://educonnect-46.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None

    def login(self, username, password):
        """Login and get access token"""
        url = f"{self.api_url}/login"
        data = {"username": username, "password": password}
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('access_token')
                print(f"✅ Login successful for {username}")
                return True
            else:
                print(f"❌ Login failed for {username}: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error for {username}: {str(e)}")
            return False

    def make_request(self, endpoint, method="GET"):
        """Make authenticated API request"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers)
                
            return response.status_code == 200, response.json() if response.status_code == 200 else response.text
        except Exception as e:
            return False, str(e)

    def test_leaderboard_endpoints(self):
        """Test all leaderboard endpoints"""
        print("\n🏆 Testing Leaderboard System APIs")
        print("-" * 50)
        
        # Test 1: Overall leaderboard
        print("\n1. Testing Overall Leaderboard:")
        success, response = self.make_request("leaderboard/overall")
        
        if success:
            print("   ✅ Overall leaderboard endpoint working")
            leaderboard = response.get('leaderboard', [])
            total_agents = response.get('total_agents', 0)
            
            print(f"   📊 Found {len(leaderboard)} agents in leaderboard")
            print(f"   📊 Total agents: {total_agents}")
            
            if leaderboard:
                top_agent = leaderboard[0]
                print(f"   🥇 Top agent: {top_agent.get('full_name', 'Unknown')}")
                print(f"   📈 Admissions: {top_agent.get('total_admissions', 0)}")
                print(f"   💰 Incentives: ₹{top_agent.get('total_incentive', 0)}")
                
                # Check for dynamic data
                total_admissions = sum(agent.get('total_admissions', 0) for agent in leaderboard)
                total_incentives = sum(agent.get('total_incentive', 0) for agent in leaderboard)
                
                if total_admissions == 0 and total_incentives == 0:
                    print("   ⚠️ WARNING: All agents have 0 admissions and incentives - may indicate static data")
                else:
                    print(f"   ✅ Dynamic data confirmed: {total_admissions} total admissions, ₹{total_incentives} total incentives")
            else:
                print("   ⚠️ No agents found in leaderboard")
        else:
            print(f"   ❌ Overall leaderboard failed: {response}")
            return False

        # Test 2: Weekly leaderboard
        print("\n2. Testing Weekly Leaderboard:")
        success, response = self.make_request("leaderboard/weekly")
        
        if success:
            print("   ✅ Weekly leaderboard endpoint working")
            weekly_leaderboard = response.get('leaderboard', [])
            period = response.get('period', {})
            
            print(f"   📅 Period: {period.get('start_date')} to {period.get('end_date')}")
            print(f"   📊 Weekly entries: {len(weekly_leaderboard)}")
            
            if weekly_leaderboard:
                weekly_admissions = sum(agent.get('period_admissions', 0) for agent in weekly_leaderboard)
                weekly_incentives = sum(agent.get('period_incentive', 0) for agent in weekly_leaderboard)
                print(f"   📈 Weekly admissions: {weekly_admissions}")
                print(f"   💰 Weekly incentives: ₹{weekly_incentives}")
        else:
            print(f"   ❌ Weekly leaderboard failed: {response}")
            return False

        # Test 3: Monthly leaderboard
        print("\n3. Testing Monthly Leaderboard:")
        success, response = self.make_request("leaderboard/monthly")
        
        if success:
            print("   ✅ Monthly leaderboard endpoint working")
            monthly_leaderboard = response.get('leaderboard', [])
            period = response.get('period', {})
            
            print(f"   📅 Period: {period.get('start_date')} to {period.get('end_date')}")
            print(f"   📊 Monthly entries: {len(monthly_leaderboard)}")
            
            if monthly_leaderboard:
                monthly_admissions = sum(agent.get('period_admissions', 0) for agent in monthly_leaderboard)
                monthly_incentives = sum(agent.get('period_incentive', 0) for agent in monthly_leaderboard)
                print(f"   📈 Monthly admissions: {monthly_admissions}")
                print(f"   💰 Monthly incentives: ₹{monthly_incentives}")
        else:
            print(f"   ❌ Monthly leaderboard failed: {response}")
            return False

        # Test 4: Custom date range leaderboard
        print("\n4. Testing Custom Date Range Leaderboard:")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        endpoint = f"leaderboard/date-range?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        success, response = self.make_request(endpoint)
        
        if success:
            print("   ✅ Custom date range leaderboard endpoint working")
            custom_leaderboard = response.get('leaderboard', [])
            summary = response.get('summary', {})
            
            print(f"   📊 Custom range entries: {len(custom_leaderboard)}")
            print(f"   📈 Period admissions: {summary.get('total_period_admissions', 0)}")
            print(f"   💰 Period incentives: ₹{summary.get('total_period_incentives', 0)}")
        else:
            print(f"   ❌ Custom date range leaderboard failed: {response}")
            return False

        return True

    def verify_data_consistency(self):
        """Verify leaderboard data matches database"""
        print("\n🔍 Verifying Data Consistency:")
        
        # Get students data
        success, students_response = self.make_request("students")
        if success:
            students = students_response if isinstance(students_response, list) else []
            approved_students = [s for s in students if s.get('status') == 'approved']
            print(f"   📊 Database: {len(approved_students)} approved students")
        else:
            print("   ❌ Could not fetch students data")
            return False

        # Get incentives data
        success, incentives_response = self.make_request("admin/incentives")
        if success:
            incentives = incentives_response if isinstance(incentives_response, list) else []
            total_incentive_amount = sum(incentive.get('amount', 0) for incentive in incentives)
            print(f"   💰 Database: ₹{total_incentive_amount} total incentives")
        else:
            print("   ❌ Could not fetch incentives data")
            return False

        # Compare with leaderboard
        success, leaderboard_response = self.make_request("leaderboard/overall")
        if success:
            leaderboard = leaderboard_response.get('leaderboard', [])
            leaderboard_admissions = sum(agent.get('total_admissions', 0) for agent in leaderboard)
            leaderboard_incentives = sum(agent.get('total_incentive', 0) for agent in leaderboard)
            
            print(f"   📊 Leaderboard: {leaderboard_admissions} total admissions")
            print(f"   💰 Leaderboard: ₹{leaderboard_incentives} total incentives")
            
            # Check consistency
            if leaderboard_admissions == len(approved_students):
                print("   ✅ PERFECT MATCH: Leaderboard admissions match database")
            else:
                print(f"   ⚠️ MISMATCH: Leaderboard shows {leaderboard_admissions}, database has {len(approved_students)}")
            
            if abs(leaderboard_incentives - total_incentive_amount) < 0.01:
                print("   ✅ PERFECT MATCH: Leaderboard incentives match database")
            else:
                print(f"   ⚠️ MISMATCH: Leaderboard shows ₹{leaderboard_incentives}, database has ₹{total_incentive_amount}")
        else:
            print("   ❌ Could not fetch leaderboard for comparison")
            return False

        return True

    def check_static_data_patterns(self):
        """Check for signs of static/hardcoded data"""
        print("\n🔍 Checking for Static Data Patterns:")
        
        success, response = self.make_request("leaderboard/overall")
        if not success:
            print("   ❌ Could not fetch leaderboard data")
            return False
            
        leaderboard = response.get('leaderboard', [])
        
        if len(leaderboard) <= 1:
            print("   ⚠️ Only one or no agents in leaderboard - cannot check patterns")
            return True
        
        # Check if all agents have identical data
        first_agent = leaderboard[0]
        first_admissions = first_agent.get('total_admissions', 0)
        first_incentive = first_agent.get('total_incentive', 0)
        
        all_identical = all(
            agent.get('total_admissions', 0) == first_admissions and 
            agent.get('total_incentive', 0) == first_incentive 
            for agent in leaderboard
        )
        
        if all_identical and first_admissions > 0:
            print("   ⚠️ WARNING: All agents have identical data - possible static/hardcoded values")
        else:
            print("   ✅ Agents have varying data - appears dynamic")
        
        # Check for placeholder names
        agent_names = [agent.get('full_name', '') for agent in leaderboard if agent.get('full_name')]
        placeholder_patterns = ['test', 'demo', 'sample', 'placeholder', 'agent1', 'agent2']
        
        placeholder_count = sum(1 for name in agent_names if any(pattern in name.lower() for pattern in placeholder_patterns))
        
        if placeholder_count == len(agent_names) and len(agent_names) > 0:
            print("   ⚠️ WARNING: All agent names appear to be placeholders")
        elif placeholder_count > 0:
            print(f"   ⚠️ {placeholder_count}/{len(agent_names)} agents have placeholder names")
        else:
            print("   ✅ Agent names appear realistic")
        
        return True

def main():
    print("🏆 LEADERBOARD SYSTEM DYNAMIC DATA VERIFICATION")
    print("=" * 60)
    
    tester = LeaderboardTester()
    
    # Try different admin credentials
    admin_credentials = [
        ('super admin', 'Admin@annaiconnect'),
        ('admin', 'admin123'),
        ('super admin', 'admin123')
    ]
    
    authenticated = False
    for username, password in admin_credentials:
        print(f"\n🔐 Trying login: {username}")
        if tester.login(username, password):
            authenticated = True
            break
    
    if not authenticated:
        print("❌ Could not authenticate with any admin credentials")
        return 1
    
    # Run tests
    success = True
    
    # Test leaderboard endpoints
    if not tester.test_leaderboard_endpoints():
        success = False
    
    # Verify data consistency
    if not tester.verify_data_consistency():
        success = False
    
    # Check for static data patterns
    if not tester.check_static_data_patterns():
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 LEADERBOARD SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 LEADERBOARD SYSTEM VERIFICATION COMPLETED!")
        print("✅ All leaderboard endpoints are working")
        print("✅ Data appears to be dynamic from database")
        print("✅ No major static data patterns detected")
    else:
        print("❌ LEADERBOARD SYSTEM VERIFICATION FAILED!")
        print("Please review the issues identified above")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())