#!/usr/bin/env python3
"""
Production Setup Script
=======================

This script sets up the production environment with the required users and courses.
"""

import requests
import sys
import json

def setup_production():
    """Setup production environment"""
    base_url = "https://admin-portal-revamp.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🚀 Setting up production environment...")
    
    # Try to setup production data directly (this endpoint might not require auth)
    try:
        response = requests.post(f"{api_url}/admin/deploy-production")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Production deployment successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            # Print created users
            production_setup = result.get('production_setup', {})
            created_users = production_setup.get('created_users', [])
            created_courses = production_setup.get('created_courses', [])
            
            print("\n👥 Created Users:")
            for user in created_users:
                print(f"   - {user}")
                
            print("\n📚 Created Courses:")
            for course in created_courses:
                print(f"   - {course}")
                
            print("\n🔐 Login Credentials:")
            print("   Admin: super admin / Admin@annaiconnect")
            print("   Coordinator: arulanantham / Arul@annaiconnect")
            print("   Agent1: agent1 / agent@123")
            print("   Agent2: agent2 / agent@123")
            print("   Agent3: agent3 / agent@123")
            
            return True
        else:
            print(f"❌ Production deployment failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up production: {str(e)}")
        return False

def test_login_after_setup():
    """Test login with production credentials"""
    base_url = "https://admin-portal-revamp.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("\n🔐 Testing login with production credentials...")
    
    # Test coordinator login
    try:
        response = requests.post(f"{api_url}/login", json={
            "username": "arulanantham",
            "password": "Arul@annaiconnect"
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Coordinator login successful!")
            print(f"   Role: {result.get('role')}")
            print(f"   User ID: {result.get('user_id')}")
            return True
        else:
            print(f"❌ Coordinator login failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🎯 PRODUCTION ENVIRONMENT SETUP")
    print("=" * 40)
    
    # Setup production environment
    if setup_production():
        print("\n✅ Production setup completed successfully!")
        
        # Test login
        if test_login_after_setup():
            print("\n🎉 Production environment is ready for signature dialog testing!")
            return 0
        else:
            print("\n⚠️ Production setup completed but login test failed")
            return 1
    else:
        print("\n❌ Production setup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())