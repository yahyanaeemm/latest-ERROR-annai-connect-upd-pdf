#!/usr/bin/env python3
"""
Bootstrap Admin User
====================

This script attempts to create an initial admin user by registering and then
manually approving the user, or by directly accessing the database.
"""

import requests
import sys
import json
from datetime import datetime

def try_register_admin():
    """Try to register an admin user"""
    base_url = "https://approval-workflow-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔐 Attempting to register admin user...")
    
    admin_data = {
        "username": "super admin",
        "email": "admin@annaiconnect.com",
        "password": "Admin@annaiconnect",
        "role": "admin",
        "first_name": "Super",
        "last_name": "Admin"
    }
    
    try:
        response = requests.post(f"{api_url}/register", json=admin_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin registration successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Admin registration failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registering admin: {str(e)}")
        return False

def try_register_coordinator():
    """Try to register a coordinator user"""
    base_url = "https://approval-workflow-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔐 Attempting to register coordinator user...")
    
    coordinator_data = {
        "username": "arulanantham",
        "email": "arul@annaiconnect.com",
        "password": "Arul@annaiconnect",
        "role": "coordinator",
        "first_name": "Arulanantham",
        "last_name": "Coordinator"
    }
    
    try:
        response = requests.post(f"{api_url}/register", json=coordinator_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Coordinator registration successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Coordinator registration failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registering coordinator: {str(e)}")
        return False

def try_register_agent():
    """Try to register an agent user"""
    base_url = "https://approval-workflow-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔐 Attempting to register agent user...")
    
    agent_data = {
        "username": "agent1",
        "email": "agent1@annaiconnect.com",
        "password": "agent@123",
        "role": "agent",
        "agent_id": "AG001",
        "first_name": "Agent",
        "last_name": "One"
    }
    
    try:
        response = requests.post(f"{api_url}/register", json=agent_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent registration successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Agent registration failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error registering agent: {str(e)}")
        return False

def test_existing_logins():
    """Test if any existing users can login"""
    base_url = "https://approval-workflow-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing existing user logins...")
    
    # Try various possible credentials
    test_credentials = [
        {"username": "super admin", "password": "Admin@annaiconnect"},
        {"username": "arulanantham", "password": "Arul@annaiconnect"},
        {"username": "agent1", "password": "agent@123"},
        {"username": "admin", "password": "admin123"},
        {"username": "coordinator", "password": "coord123"},
        {"username": "agent1", "password": "agent123"},
    ]
    
    for creds in test_credentials:
        try:
            response = requests.post(f"{api_url}/login", json=creds)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Login successful: {creds['username']}")
                print(f"   Role: {result.get('role')}")
                print(f"   User ID: {result.get('user_id')}")
                return creds, result.get('access_token')
            else:
                print(f"❌ Login failed for {creds['username']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing login for {creds['username']}: {str(e)}")
    
    return None, None

def main():
    """Main bootstrap function"""
    print("🎯 BOOTSTRAP ADMIN USER")
    print("=" * 30)
    
    # First, test if any existing users can login
    creds, token = test_existing_logins()
    
    if creds and token:
        print(f"\n✅ Found working credentials: {creds['username']}")
        print("🎉 Ready for signature dialog testing!")
        return 0
    
    print("\n📝 No existing users found. Attempting to register users...")
    
    # Try to register users
    admin_registered = try_register_admin()
    coordinator_registered = try_register_coordinator()
    agent_registered = try_register_agent()
    
    if admin_registered or coordinator_registered or agent_registered:
        print("\n✅ User registration completed!")
        print("⚠️  Note: Users are pending admin approval in the new system.")
        print("   You may need to manually approve them or use a different approach.")
        return 0
    else:
        print("\n❌ Failed to register any users")
        print("⚠️  The database might be empty or there might be an issue with the system.")
        return 1

if __name__ == "__main__":
    sys.exit(main())