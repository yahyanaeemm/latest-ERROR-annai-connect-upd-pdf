#!/usr/bin/env python3
"""
Final Production Deployment Test
"""

import requests
import json

def final_production_test():
    """Final comprehensive test"""
    base_url = "https://educonnect-46.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 FINAL PRODUCTION DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    # Test with production admin credentials (should exist after deployment)
    print("\n🔐 Testing with production admin credentials")
    login_response = requests.post(
        f"{api_url}/login",
        json={"username": "super admin", "password": "Admin@annaiconnect"}
    )
    
    if login_response.status_code != 200:
        print("❌ Production admin login failed")
        return False
    
    admin_token = login_response.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    print("✅ Production admin authenticated")
    
    # Test 1: Verify production system is ready
    print("\n📋 TEST 1: Production System Verification")
    print("-" * 45)
    
    # Check admin dashboard
    dashboard_response = requests.get(f"{api_url}/admin/dashboard-enhanced", headers=admin_headers)
    if dashboard_response.status_code != 200:
        print("❌ Admin dashboard not accessible")
        return False
    print("   ✅ Admin dashboard accessible")
    
    # Check courses
    courses_response = requests.get(f"{api_url}/incentive-rules")
    if courses_response.status_code != 200:
        print("❌ Courses not accessible")
        return False
    
    courses = courses_response.json()
    expected_courses = {"B.Ed": 6000.0, "MBA": 2500.0, "BNYS": 20000.0}
    
    for course in courses:
        course_name = course.get('course')
        if course_name in expected_courses:
            expected_amount = expected_courses[course_name]
            actual_amount = course.get('amount')
            if actual_amount == expected_amount:
                print(f"   ✅ {course_name}: ₹{actual_amount}")
            else:
                print(f"❌ {course_name}: wrong amount")
                return False
    
    # Test 2: Verify all production users
    print("\n📋 TEST 2: Production Users Verification")
    print("-" * 45)
    
    production_users = [
        {"username": "super admin", "password": "Admin@annaiconnect", "role": "admin"},
        {"username": "arulanantham", "password": "Arul@annaiconnect", "role": "coordinator"},
        {"username": "agent1", "password": "agent@123", "role": "agent"},
        {"username": "agent2", "password": "agent@123", "role": "agent"},
        {"username": "agent3", "password": "agent@123", "role": "agent"}
    ]
    
    for user in production_users:
        login_test = requests.post(
            f"{api_url}/login",
            json={"username": user['username'], "password": user['password']}
        )
        
        if login_test.status_code != 200:
            print(f"❌ {user['username']} login failed")
            return False
        
        user_data = login_test.json()
        if user_data.get('role') != user['role']:
            print(f"❌ {user['username']} wrong role")
            return False
        
        print(f"   ✅ {user['username']} ({user['role']}) verified")
    
    # Test 3: Test another deployment call (should work)
    print("\n📋 TEST 3: Repeated Deployment Test")
    print("-" * 40)
    
    deploy_response = requests.post(f"{api_url}/admin/deploy-production", headers=admin_headers)
    
    if deploy_response.status_code != 200:
        print(f"❌ Repeated deployment failed: {deploy_response.status_code}")
        return False
    
    deploy_data = deploy_response.json()
    print("   ✅ Repeated deployment handled correctly")
    print(f"   Status: {deploy_data.get('status')}")
    
    print("\n🎉 ALL ERROR HANDLING TESTS PASSED!")
    print("✅ Production deployment system is robust and ready")
    
    return True

if __name__ == "__main__":
    if final_production_test():
        print("\n📊 FINAL RESULT: SUCCESS")
        exit(0)
    else:
        print("\n📊 FINAL RESULT: FAILED")
        exit(1)