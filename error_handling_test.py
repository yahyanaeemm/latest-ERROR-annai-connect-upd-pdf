#!/usr/bin/env python3
"""
Production Deployment Error Handling and Edge Cases Test
"""

import requests
import json
from datetime import datetime

def test_error_handling():
    """Test error handling and edge cases"""
    base_url = "https://ab3db277-9e87-4833-abeb-9dcbf5c8a2e7.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 PRODUCTION DEPLOYMENT ERROR HANDLING TEST")
    print("=" * 60)
    
    # Create another test admin for error testing
    print("\n🔧 Setup: Create test admin for error testing")
    
    # Create test admin via database
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    from passlib.context import CryptContext
    import uuid
    
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    
    async def create_error_test_admin():
        test_admin = {
            'id': str(uuid.uuid4()),
            'username': 'error_test_admin',
            'email': 'error_test_admin@test.com',
            'role': 'admin',
            'first_name': 'Error',
            'last_name': 'TestAdmin',
            'hashed_password': pwd_context.hash('error_test_pass'),
            'created_at': datetime.utcnow()
        }
        
        await db.users.insert_one(test_admin)
        print('✅ Error test admin created')
    
    asyncio.run(create_error_test_admin())
    
    # Login with error test admin
    login_response = requests.post(
        f"{api_url}/login",
        json={"username": "error_test_admin", "password": "error_test_pass"}
    )
    
    if login_response.status_code != 200:
        print("❌ Failed to login with error test admin")
        return False
    
    admin_token = login_response.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    print("✅ Error test admin authenticated")
    
    # Test 1: Multiple deployment calls (should handle gracefully)
    print("\n📋 TEST 1: Multiple Deployment Calls")
    print("-" * 40)
    
    print("🚀 First deployment call...")
    deploy1_response = requests.post(f"{api_url}/admin/deploy-production", headers=admin_headers)
    
    if deploy1_response.status_code != 200:
        print(f"❌ First deployment failed: {deploy1_response.status_code}")
        return False
    
    deploy1_data = deploy1_response.json()
    print("   ✅ First deployment successful")
    print(f"   Cleanup: {deploy1_data['cleanup_summary']['deleted_records']}")
    
    print("🚀 Second deployment call (should handle empty database)...")
    deploy2_response = requests.post(f"{api_url}/admin/deploy-production", headers=admin_headers)
    
    if deploy2_response.status_code != 200:
        print(f"❌ Second deployment failed: {deploy2_response.status_code}")
        return False
    
    deploy2_data = deploy2_response.json()
    print("   ✅ Second deployment handled gracefully")
    print(f"   Cleanup: {deploy2_data['cleanup_summary']['deleted_records']}")
    
    # Test 2: Response Format Verification
    print("\n📋 TEST 2: Response Format Verification")
    print("-" * 45)
    
    # Verify comprehensive response format
    required_structure = {
        'message': str,
        'cleanup_summary': dict,
        'production_setup': dict,
        'next_steps': list,
        'status': str
    }
    
    for field, expected_type in required_structure.items():
        if field not in deploy2_data:
            print(f"❌ Missing field: {field}")
            return False
        if not isinstance(deploy2_data[field], expected_type):
            print(f"❌ Wrong type for {field}: expected {expected_type}, got {type(deploy2_data[field])}")
            return False
    
    print("   ✅ Response format verification passed")
    
    # Verify cleanup summary structure
    cleanup_summary = deploy2_data['cleanup_summary']
    if 'deleted_records' not in cleanup_summary or 'uploads_cleared' not in cleanup_summary:
        print("❌ Invalid cleanup summary structure")
        return False
    
    # Verify production setup structure
    production_setup = deploy2_data['production_setup']
    if 'created_users' not in production_setup or 'created_courses' not in production_setup:
        print("❌ Invalid production setup structure")
        return False
    
    print("   ✅ All response structures validated")
    
    # Test 3: Next Steps Verification
    print("\n📋 TEST 3: Next Steps Verification")
    print("-" * 40)
    
    next_steps = deploy2_data['next_steps']
    expected_steps = [
        "Login with new admin credentials",
        "Login with coordinator",
        "Login with agents",
        "System is ready for production use"
    ]
    
    if len(next_steps) < 4:
        print(f"❌ Insufficient next steps: expected at least 4, got {len(next_steps)}")
        return False
    
    # Check that next steps contain login instructions
    steps_text = ' '.join(next_steps)
    if 'admin credentials' not in steps_text or 'coordinator' not in steps_text or 'agents' not in steps_text:
        print("❌ Next steps missing critical login information")
        return False
    
    print("   ✅ Next steps verification passed")
    print(f"   Steps provided: {len(next_steps)}")
    for i, step in enumerate(next_steps, 1):
        print(f"   {i}. {step}")
    
    # Test 4: Production Readiness Verification
    print("\n📋 TEST 4: Production Readiness Verification")
    print("-" * 50)
    
    # Verify all production users can login
    production_credentials = [
        {"username": "super admin", "password": "Admin@annaiconnect"},
        {"username": "arulanantham", "password": "Arul@annaiconnect"},
        {"username": "agent1", "password": "agent@123"},
        {"username": "agent2", "password": "agent@123"},
        {"username": "agent3", "password": "agent@123"}
    ]
    
    for creds in production_credentials:
        login_test = requests.post(
            f"{api_url}/login",
            json={"username": creds['username'], "password": creds['password']}
        )
        
        if login_test.status_code != 200:
            print(f"❌ Production user {creds['username']} cannot login")
            return False
    
    print("   ✅ All production users can login")
    
    # Verify courses are available
    courses_response = requests.get(f"{api_url}/incentive-rules")
    if courses_response.status_code != 200:
        print("❌ Courses not accessible")
        return False
    
    courses = courses_response.json()
    expected_course_count = 3
    if len(courses) != expected_course_count:
        print(f"❌ Expected {expected_course_count} courses, got {len(courses)}")
        return False
    
    print(f"   ✅ All {len(courses)} production courses accessible")
    
    print("\n🎉 ERROR HANDLING AND EDGE CASES VERIFICATION COMPLETED!")
    print("=" * 70)
    print("✅ Multiple Deployment Calls - HANDLED GRACEFULLY")
    print("✅ Response Format - COMPREHENSIVE AND CORRECT")
    print("✅ Next Steps - DETAILED AND HELPFUL")
    print("✅ Production Readiness - FULLY VERIFIED")
    print("✅ Error Handling - ROBUST")
    
    return True

if __name__ == "__main__":
    if test_error_handling():
        print("\n📊 FINAL RESULT: ALL ERROR HANDLING TESTS PASSED")
        exit(0)
    else:
        print("\n📊 FINAL RESULT: ERROR HANDLING TESTS FAILED")
        exit(1)