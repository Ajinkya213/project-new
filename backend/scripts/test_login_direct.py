#!/usr/bin/env python3
"""
Test login endpoint directly
"""

import requests
import json

def test_login_direct():
    """Test login endpoint directly"""
    base_url = "http://localhost:8000"
    
    print("🔐 Testing login endpoint directly...")
    
    # Test data
    login_data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    try:
        # Test OPTIONS request (CORS preflight)
        print("1. Testing OPTIONS request...")
        options_response = requests.options(f"{base_url}/auth/login")
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        
        # Test POST request
        print("\n2. Testing POST request...")
        post_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        print(f"POST Status: {post_response.status_code}")
        print(f"POST Headers: {dict(post_response.headers)}")
        print(f"POST Response: {post_response.text}")
        
        if post_response.status_code == 200:
            print("✅ Login successful!")
            data = post_response.json()
            if 'tokens' in data:
                print("✅ Tokens received!")
            else:
                print("❌ No tokens in response")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cors_headers():
    """Test CORS headers"""
    base_url = "http://localhost:8000"
    
    print("\n🌐 Testing CORS headers...")
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Status: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_direct()
    test_cors_headers() 