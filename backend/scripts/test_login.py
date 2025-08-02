#!/usr/bin/env python3
"""
Test login functionality
"""

import requests
import json

def test_login():
    """Test login functionality"""
    base_url = "http://localhost:8000"
    
    print("🔐 Testing login functionality...")
    
    # Test data - use the user we just created
    test_user = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    try:
        # Test login directly (user already exists)
        print("🔑 Testing user login...")
        
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            response_data = login_response.json()
            if 'tokens' in response_data:
                print("✅ Tokens received")
                print(f"Access token: {response_data['tokens']['access_token'][:50]}...")
                return True
            else:
                print("❌ No tokens in response")
                return False
        else:
            print("❌ Login failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is the backend running?")
        print("💡 Start the backend with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_server_health():
    """Test if server is running"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False

def test_registration():
    """Test user registration"""
    base_url = "http://localhost:8000"
    
    print("📝 Testing user registration...")
    
    # Test data for new user
    new_user = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123!"
    }
    
    try:
        register_response = requests.post(
            f"{base_url}/auth/register",
            json=new_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Register status: {register_response.status_code}")
        if register_response.status_code == 201:
            print("✅ Registration successful")
            return True
        else:
            print(f"❌ Registration failed: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting login test...")
    
    # First check if server is running
    if not test_server_health():
        print("\n💡 To start the server:")
        print("1. cd backend")
        print("2. python app.py")
        exit(1)
    
    # Test registration
    print("\n" + "="*50)
    registration_success = test_registration()
    
    # Test login
    print("\n" + "="*50)
    login_success = test_login()
    
    if login_success:
        print("\n🎉 Login functionality is working!")
        print("\n📋 Test Credentials:")
        print("Username: testuser")
        print("Password: TestPass123!")
    else:
        print("\n⚠️ Login functionality has issues. Check the output above.") 