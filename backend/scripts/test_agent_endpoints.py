#!/usr/bin/env python3
"""
Test agent endpoints
"""

import requests
import json

def test_agent_endpoints():
    """Test agent endpoints"""
    base_url = "http://localhost:8000"
    
    print("🤖 Testing agent endpoints...")
    
    # Test agent health endpoint
    print("\n1. Testing agent health endpoint...")
    try:
        response = requests.get(f"{base_url}/agent/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test agent query endpoint (without auth)
    print("\n2. Testing agent query endpoint (without auth)...")
    try:
        response = requests.post(
            f"{base_url}/agent/query",
            json={"query": "Hello", "agent_type": "lightweight"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test agent test endpoint
    print("\n3. Testing agent test endpoint...")
    try:
        response = requests.post(
            f"{base_url}/agent/test",
            json={"query": "Hello"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with authentication
    print("\n4. Testing with authentication...")
    try:
        # First login to get token
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            tokens = login_response.json()["tokens"]
            access_token = tokens["access_token"]
            
            print("✅ Login successful, testing authenticated agent query...")
            
            # Test authenticated agent query
            response = requests.post(
                f"{base_url}/agent/query",
                json={"query": "Hello", "agent_type": "lightweight"},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_agent_endpoints() 