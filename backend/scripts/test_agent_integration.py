#!/usr/bin/env python3
"""
Test script for agent integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_agent_health():
    """Test agent health endpoint"""
    print("Testing agent health...")
    try:
        response = requests.get(f"{BASE_URL}/agent/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_agent_status():
    """Test agent status endpoint"""
    print("\nTesting agent status...")
    try:
        response = requests.get(f"{BASE_URL}/agent/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check passed: {data}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_agent_query():
    """Test agent query endpoint"""
    print("\nTesting agent query...")
    try:
        # First get a test token (you might need to adjust this)
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        
        # Try to login or use a test token
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
        else:
            print("⚠️  Could not get auth token, testing without auth...")
            token = None
        
        # Test query
        query_data = {
            "query": "Hello, how are you?",
            "agent_type": "lightweight"
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.post(f"{BASE_URL}/agent/query", json=query_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query test passed: {data}")
            return True
        else:
            print(f"❌ Query test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Query test error: {e}")
        return False

def test_agent_stats():
    """Test agent stats endpoint"""
    print("\nTesting agent stats...")
    try:
        response = requests.get(f"{BASE_URL}/agent/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats check passed: {data}")
            return True
        else:
            print(f"❌ Stats check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Agent Integration")
    print("=" * 40)
    
    tests = [
        test_agent_health,
        test_agent_status,
        test_agent_query,
        test_agent_stats
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent integration is working.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 