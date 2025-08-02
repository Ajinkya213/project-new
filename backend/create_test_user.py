#!/usr/bin/env python3
"""
Create a test user for authentication testing
"""

import requests
import json

def create_test_user():
    """Create a test user"""
    print("👤 Creating Test User")
    print("=" * 50)
    
    # Test user data
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Test user created successfully")
            print(f"👤 Username: {user_data['username']}")
            print(f"📧 Email: {user_data['email']}")
            print(f"🎫 Access token: {result.get('tokens', {}).get('access_token', 'NOT_FOUND')[:20]}...")
            return result.get('tokens', {}).get('access_token')
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_login_with_created_user():
    """Test login with the created user"""
    print("\n🔐 Testing Login with Created User")
    print("=" * 50)
    
    login_data = {
        "username": "testuser2",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            print(f"🎫 Access token: {result.get('access_token', 'NOT_FOUND')[:20]}...")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def main():
    """Main function"""
    print("👤 Test User Creation")
    print("=" * 50)
    
    # Create test user
    token = create_test_user()
    
    if token:
        # Test login
        login_token = test_login_with_created_user()
        
        print("\n📊 Test User Summary")
        print("=" * 50)
        print(f"User Creation: {'✅' if token else '❌'}")
        print(f"Login Test: {'✅' if login_token else '❌'}")
        
        if token and login_token:
            print("\n🎉 Test user setup complete!")
            print("You can now use these credentials in the frontend:")
            print("Username: testuser")
            print("Password: testpassword123")
        else:
            print("\n⚠️  Some tests failed")
    else:
        print("\n❌ Test user creation failed")

if __name__ == "__main__":
    main() 