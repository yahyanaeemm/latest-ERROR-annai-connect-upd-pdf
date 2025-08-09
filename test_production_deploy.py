#!/usr/bin/env python3
"""
Combined Production Deployment System Test
"""

import requests
import json
from datetime import datetime

def test_combined_production_deployment():
    """Test the combined production deployment system"""
    base_url = "https://ab3db277-9e87-4833-abeb-9dcbf5c8a2e7.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 COMBINED PRODUCTION DEPLOYMENT SYSTEM TEST")
    print("=" * 60)
    
    # Step 1: Login with test admin
    print("\n🔐 Step 1: Login with test admin")
    login_response = requests.post(
        f"{api_url}/login",
        json={"username": "test_admin", "password": "test_admin_pass"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login: {login_response.status_code}")
        try:
            print(f"   Error: {login_response.json()}")
        except:
            print(f"   Response: {login_response.text}")
        return False
    
    admin_token = login_response.json()['access_token']
    print("✅ Test admin logged in successfully")
    
    # Step 2: Test access control
    print("\n🔒 Step 2: Test access control")
    unauth_response = requests.post(f"{api_url}/admin/deploy-production")
    
    if unauth_response.status_code != 403:
        print(f"❌ Expected 403 for unauthenticated request, got {unauth_response.status_code}")
        return False
    
    print("✅ Unauthenticated access properly denied")
    
    # Step 3: Test combined production deployment
    print("\n🚀 Step 3: Test combined production deployment")
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    deploy_response = requests.post(
        f"{api_url}/admin/deploy-production",
        headers=headers
    )
    
    if deploy_response.status_code != 200:
        print(f"❌ Deploy production failed: {deploy_response.status_code}")
        try:
            print(f"   Error: {deploy_response.json()}")
        except:
            print(f"   Response: {deploy_response.text}")
        return False
    
    deploy_data = deploy_response.json()
    print("✅ Combined deployment completed successfully")
    
    # Verify response structure
    required_fields = ['message', 'cleanup_summary', 'production_setup', 'next_steps', 'status']
    for field in required_fields:
        if field not in deploy_data:
            print(f"❌ Missing required field '{field}' in response")
            return False
    
    print(f"   Message: {deploy_data['message']}")
    print(f"   Cleanup: {deploy_data['cleanup_summary']['deleted_records']}")
    print(f"   Created users: {deploy_data['production_setup']['created_users']}")
    print(f"   Created courses: {deploy_data['production_setup']['created_courses']}")
    
    # Step 4: Test production users login
    print("\n🔐 Step 4: Test production users login")
    production_credentials = [
        {"username": "super admin", "password": "Admin@annaiconnect", "role": "admin"},
        {"username": "arulanantham", "password": "Arul@annaiconnect", "role": "coordinator"},
        {"username": "agent1", "password": "agent@123", "role": "agent"},
        {"username": "agent2", "password": "agent@123", "role": "agent"},
        {"username": "agent3", "password": "agent@123", "role": "agent"}
    ]
    
    production_tokens = {}
    for creds in production_credentials:
        login_response = requests.post(
            f"{api_url}/login",
            json={"username": creds['username'], "password": creds['password']}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login {creds['username']}: {login_response.status_code}")
            return False
        
        login_data = login_response.json()
        if login_data.get('role') != creds['role']:
            print(f"❌ Wrong role for {creds['username']}: expected {creds['role']}, got {login_data.get('role')}")
            return False
        
        production_tokens[creds['username']] = login_data['access_token']
        print(f"   ✅ {creds['username']} login successful - Role: {creds['role']}")
    
    # Step 5: Test production courses availability
    print("\n📚 Step 5: Test production courses availability")
    courses_response = requests.get(f"{api_url}/incentive-rules")
    
    if courses_response.status_code != 200:
        print(f"❌ Failed to get courses: {courses_response.status_code}")
        return False
    
    courses = courses_response.json()
    expected_courses = {"B.Ed": 6000.0, "MBA": 2500.0, "BNYS": 20000.0}
    
    for course in courses:
        course_name = course.get('course')
        if course_name in expected_courses:
            expected_amount = expected_courses[course_name]
            actual_amount = course.get('amount')
            if actual_amount == expected_amount:
                print(f"   ✅ {course_name}: ₹{actual_amount} incentive verified")
            else:
                print(f"❌ {course_name}: expected ₹{expected_amount}, got ₹{actual_amount}")
                return False
    
    # Step 6: Test role-based access
    print("\n🎭 Step 6: Test role-based access")
    
    # Test admin dashboard access
    admin_headers = {'Authorization': f'Bearer {production_tokens["super admin"]}'}
    admin_response = requests.get(f"{api_url}/admin/dashboard-enhanced", headers=admin_headers)
    
    if admin_response.status_code != 200:
        print(f"❌ Admin dashboard access failed: {admin_response.status_code}")
        return False
    print("   ✅ Admin dashboard access working")
    
    # Test coordinator access
    coord_headers = {'Authorization': f'Bearer {production_tokens["arulanantham"]}'}
    coord_response = requests.get(f"{api_url}/students/paginated", headers=coord_headers)
    
    if coord_response.status_code != 200:
        print(f"❌ Coordinator access failed: {coord_response.status_code}")
        return False
    print("   ✅ Coordinator access working")
    
    # Test agent access
    agent_headers = {'Authorization': f'Bearer {production_tokens["agent1"]}'}
    agent_response = requests.get(f"{api_url}/students", headers=agent_headers)
    
    if agent_response.status_code != 200:
        print(f"❌ Agent access failed: {agent_response.status_code}")
        return False
    print("   ✅ Agent access working")
    
    # Step 7: Test student creation workflow
    print("\n👨‍🎓 Step 7: Test student creation workflow")
    
    student_data = {
        "first_name": "Production",
        "last_name": "TestStudent",
        "email": f"prod.test.{datetime.now().strftime('%H%M%S')}@annaiconnect.com",
        "phone": "9876543210",
        "course": "B.Ed"
    }
    
    student_response = requests.post(
        f"{api_url}/students",
        json=student_data,
        headers=agent_headers
    )
    
    if student_response.status_code != 200:
        print(f"❌ Student creation failed: {student_response.status_code}")
        return False
    
    student_data_response = student_response.json()
    token_number = student_data_response.get('token_number')
    
    if not token_number or not token_number.startswith('AGI'):
        print(f"❌ Invalid token format: {token_number}")
        return False
    
    print(f"   ✅ Production student created with AGI token: {token_number}")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Combined Production Deployment System fully verified")
    print("✅ System ready for production use")
    return True

if __name__ == "__main__":
    if test_combined_production_deployment():
        print("\n📊 FINAL RESULT: SUCCESS")
        exit(0)
    else:
        print("\n📊 FINAL RESULT: FAILED")
        exit(1)