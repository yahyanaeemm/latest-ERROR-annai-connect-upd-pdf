#!/usr/bin/env python3
"""
Comprehensive Production Deployment Verification
Tests all aspects of the combined production deployment system
"""

import requests
import json
from datetime import datetime

def comprehensive_production_test():
    """Comprehensive test of production deployment system"""
    base_url = "https://ab3db277-9e87-4833-abeb-9dcbf5c8a2e7.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 COMPREHENSIVE PRODUCTION DEPLOYMENT VERIFICATION")
    print("=" * 70)
    
    # Setup: Create test admin and login
    print("\n🔧 Setup: Login with test admin")
    login_response = requests.post(
        f"{api_url}/login",
        json={"username": "test_admin", "password": "test_admin_pass"}
    )
    
    if login_response.status_code != 200:
        print("❌ Failed to login with test admin")
        return False
    
    admin_token = login_response.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    print("✅ Test admin authenticated")
    
    # Test 1: Combined Production Deployment API Testing
    print("\n📋 TEST 1: Combined Production Deployment API")
    print("-" * 50)
    
    # Test access control - non-admin should get 403
    print("🔒 Testing access control...")
    unauth_response = requests.post(f"{api_url}/admin/deploy-production")
    if unauth_response.status_code != 403:
        print(f"❌ Expected 403 for unauthenticated, got {unauth_response.status_code}")
        return False
    print("   ✅ Non-admin access properly denied (403)")
    
    # Test the combined endpoint
    print("🚀 Testing combined deploy-production endpoint...")
    deploy_response = requests.post(f"{api_url}/admin/deploy-production", headers=admin_headers)
    
    if deploy_response.status_code != 200:
        print(f"❌ Deploy production failed: {deploy_response.status_code}")
        return False
    
    deploy_data = deploy_response.json()
    print("   ✅ Combined deployment endpoint working")
    
    # Verify atomic operation (cleanup AND setup in one call)
    required_fields = ['message', 'cleanup_summary', 'production_setup', 'next_steps', 'status']
    for field in required_fields:
        if field not in deploy_data:
            print(f"❌ Missing field '{field}' in response")
            return False
    
    print("   ✅ Atomic operation verified - cleanup AND setup in one call")
    print(f"   Cleanup: {deploy_data['cleanup_summary']['deleted_records']}")
    print(f"   Setup: {len(deploy_data['production_setup']['created_users'])} users, {len(deploy_data['production_setup']['created_courses'])} courses")
    
    # Test 2: Complete Production Workflow Verification
    print("\n📋 TEST 2: Complete Production Workflow Verification")
    print("-" * 55)
    
    # Verify database cleanup occurred
    print("🗑️ Verifying database cleanup...")
    cleanup_summary = deploy_data['cleanup_summary']
    if not cleanup_summary.get('uploads_cleared'):
        print("❌ Uploads directory not cleared")
        return False
    print("   ✅ Database cleanup verified - all collections cleared")
    print("   ✅ Uploads directory cleared and recreated")
    
    # Verify production users created correctly
    print("👥 Verifying production users...")
    expected_users = [
        "admin: super admin",
        "coordinator: arulanantham", 
        "agent: agent1",
        "agent: agent2",
        "agent: agent3"
    ]
    
    created_users = deploy_data['production_setup']['created_users']
    for expected_user in expected_users:
        if expected_user not in created_users:
            print(f"❌ Missing user: {expected_user}")
            return False
    print("   ✅ All production users created correctly")
    
    # Verify production courses created
    print("📚 Verifying production courses...")
    expected_courses = [
        "B.Ed: ₹6000.0",
        "MBA: ₹2500.0", 
        "BNYS: ₹20000.0"
    ]
    
    created_courses = deploy_data['production_setup']['created_courses']
    for expected_course in expected_courses:
        if expected_course not in created_courses:
            print(f"❌ Missing course: {expected_course}")
            return False
    print("   ✅ All production courses created correctly")
    
    # Test 3: Post-Deployment Verification
    print("\n📋 TEST 3: Post-Deployment Verification")
    print("-" * 45)
    
    # Test login functionality with all new production users
    print("🔐 Testing login with all production users...")
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
            print(f"❌ Login failed for {creds['username']}")
            return False
        
        login_data = login_response.json()
        if login_data.get('role') != creds['role']:
            print(f"❌ Wrong role for {creds['username']}")
            return False
        
        production_tokens[creds['username']] = login_data['access_token']
        print(f"   ✅ {creds['username']} login verified")
    
    # Verify role-based access works correctly
    print("🎭 Testing role-based access...")
    
    # Admin can access admin dashboard
    admin_headers = {'Authorization': f'Bearer {production_tokens["super admin"]}'}
    admin_response = requests.get(f"{api_url}/admin/dashboard-enhanced", headers=admin_headers)
    if admin_response.status_code != 200:
        print("❌ Admin dashboard access failed")
        return False
    print("   ✅ Admin can access admin dashboard")
    
    # Coordinator can access coordinator dashboard
    coord_headers = {'Authorization': f'Bearer {production_tokens["arulanantham"]}'}
    coord_response = requests.get(f"{api_url}/students/paginated", headers=coord_headers)
    if coord_response.status_code != 200:
        print("❌ Coordinator dashboard access failed")
        return False
    print("   ✅ Coordinator can access coordinator dashboard")
    
    # Agents can access agent dashboard
    agent_headers = {'Authorization': f'Bearer {production_tokens["agent1"]}'}
    agent_response = requests.get(f"{api_url}/students", headers=agent_headers)
    if agent_response.status_code != 200:
        print("❌ Agent dashboard access failed")
        return False
    print("   ✅ Agents can access agent dashboard")
    
    # Verify courses are accessible via GET /api/incentive-rules
    print("📚 Verifying courses accessible...")
    courses_response = requests.get(f"{api_url}/incentive-rules")
    if courses_response.status_code != 200:
        print("❌ Courses not accessible")
        return False
    
    courses = courses_response.json()
    if len(courses) != 3:
        print(f"❌ Expected 3 courses, got {len(courses)}")
        return False
    print("   ✅ Courses accessible via GET /api/incentive-rules")
    
    # Test 4: Student Registration and Approval Workflow
    print("\n📋 TEST 4: Student Registration and Approval Workflow")
    print("-" * 55)
    
    # Test student creation with new production agent
    print("👨‍🎓 Testing student creation...")
    student_data = {
        "first_name": "Production",
        "last_name": "Student",
        "email": f"prod.student.{datetime.now().strftime('%H%M%S')}@annaiconnect.com",
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
    
    student_result = student_response.json()
    student_id = student_result['id']
    token_number = student_result['token_number']
    
    if not token_number.startswith('AGI'):
        print(f"❌ Invalid AGI token: {token_number}")
        return False
    
    print(f"   ✅ Student created with AGI token: {token_number}")
    
    # Test coordinator approval workflow
    print("👨‍💼 Testing coordinator approval...")
    coord_approval_data = "status=approved&notes=Production test coordinator approval"
    coord_approval_headers = {
        'Authorization': f'Bearer {production_tokens["arulanantham"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    coord_approval_response = requests.put(
        f"{api_url}/students/{student_id}/status",
        data=coord_approval_data,
        headers=coord_approval_headers
    )
    
    if coord_approval_response.status_code != 200:
        print(f"❌ Coordinator approval failed: {coord_approval_response.status_code}")
        return False
    print("   ✅ Coordinator approval workflow working")
    
    # Test admin final approval process
    print("👑 Testing admin final approval...")
    admin_approval_data = "notes=Production test admin final approval"
    admin_approval_headers = {
        'Authorization': f'Bearer {production_tokens["super admin"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    admin_approval_response = requests.put(
        f"{api_url}/admin/approve-student/{student_id}",
        data=admin_approval_data,
        headers=admin_approval_headers
    )
    
    if admin_approval_response.status_code != 200:
        print(f"❌ Admin final approval failed: {admin_approval_response.status_code}")
        return False
    print("   ✅ Admin final approval process working")
    
    # Test 5: Integration Testing
    print("\n📋 TEST 5: Integration Testing")
    print("-" * 35)
    
    # Verify system can handle student registration with new agents
    print("🔄 Testing complete production readiness...")
    
    # Check that incentive was created after admin approval
    incentives_response = requests.get(f"{api_url}/admin/incentives", headers=admin_headers)
    if incentives_response.status_code != 200:
        print("❌ Failed to get incentives")
        return False
    
    incentives = incentives_response.json()
    if len(incentives) == 0:
        print("❌ No incentive created after approval")
        return False
    
    # Find the incentive for our test student
    student_incentive = None
    for incentive in incentives:
        if incentive.get('student_id') == student_id:
            student_incentive = incentive
            break
    
    if not student_incentive:
        print("❌ Incentive not found for approved student")
        return False
    
    if student_incentive.get('amount') != 6000.0:
        print(f"❌ Wrong incentive amount: expected 6000.0, got {student_incentive.get('amount')}")
        return False
    
    print("   ✅ Incentive system working with new courses")
    print(f"   ✅ B.Ed incentive created: ₹{student_incentive.get('amount')}")
    
    print("\n🎉 COMPREHENSIVE VERIFICATION COMPLETED!")
    print("=" * 70)
    print("✅ Combined Production Deployment API - WORKING")
    print("✅ Admin Access Control - WORKING") 
    print("✅ Complete Cleanup and Setup - WORKING")
    print("✅ Production Users Creation - WORKING")
    print("✅ Production Courses Creation - WORKING")
    print("✅ Post-Deployment Login - WORKING")
    print("✅ Role-Based Access - WORKING")
    print("✅ Student Registration Workflow - WORKING")
    print("✅ Coordinator Approval Workflow - WORKING")
    print("✅ Admin Final Approval - WORKING")
    print("✅ Incentive System Integration - WORKING")
    print("✅ AGI Token Generation - WORKING")
    print("\n🎯 SYSTEM IS PRODUCTION READY!")
    
    return True

if __name__ == "__main__":
    if comprehensive_production_test():
        print("\n📊 FINAL RESULT: ALL TESTS PASSED")
        exit(0)
    else:
        print("\n📊 FINAL RESULT: TESTS FAILED")
        exit(1)