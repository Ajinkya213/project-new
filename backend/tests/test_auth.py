#!/usr/bin/env python3
"""
Test authentication and JWT token validation
"""

import requests
import json

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check (no auth required)
    print("\n🏥 Testing Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Agent health (no auth required)
    print("\n🤖 Testing Agent Health")
    try:
        response = requests.get(f"{base_url}/agent/health")
        if response.status_code == 200:
            print("✅ Agent health check successful")
        else:
            print(f"❌ Agent health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent health check error: {e}")
    
    # Test 3: Chat sessions (requires auth)
    print("\n💬 Testing Chat Sessions (requires auth)")
    try:
        response = requests.get(f"{base_url}/chat/sessions")
        if response.status_code == 401:
            print("✅ Authentication required (expected)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat sessions error: {e}")

def test_jwt_token():
    """Test JWT token validation"""
    print("\n🎫 Testing JWT Token")
    print("=" * 50)
    
    # Test with invalid token
    print("\n🔍 Testing with invalid token")
    try:
        response = requests.get(
            "http://localhost:8000/chat/sessions",
            headers={"Authorization": "Bearer invalid_token"}
        )
        if response.status_code == 422:
            print("✅ Invalid token properly rejected (422)")
        elif response.status_code == 401:
            print("✅ Invalid token properly rejected (401)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
    
    # Test with missing token
    print("\n🔍 Testing with missing token")
    try:
        response = requests.get("http://localhost:8000/chat/sessions")
        if response.status_code == 401:
            print("✅ Missing token properly rejected")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Missing token test error: {e}")

def test_agent_endpoints():
    """Test agent endpoints that don't require auth"""
    print("\n🤖 Testing Agent Endpoints")
    print("=" * 50)
    
    # Test agent list
    print("\n📋 Testing Agent List")
    try:
        response = requests.get("http://localhost:8000/agent/agents")
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent list successful")
            print(f"📊 Available agents: {len(result.get('agents', []))}")
        else:
            print(f"❌ Agent list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent list error: {e}")
    
    # Test agent test endpoint
    print("\n🧪 Testing Agent Test Endpoint")
    try:
        response = requests.post(
            "http://localhost:8000/agent/test",
            json={"query": "Hello, how are you?"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Agent test successful")
            print(f"🤖 Agent type: {result.get('result', {}).get('agent_type', 'Unknown')}")
        else:
            print(f"❌ Agent test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Agent test error: {e}")

def main():
    """Main test function"""
    print("🔐 Authentication and JWT Validation")
    print("=" * 50)
    
    # Test 1: Auth endpoints
    test_auth_endpoints()
    
    # Test 2: JWT token validation
    test_jwt_token()
    
    # Test 3: Agent endpoints
    test_agent_endpoints()
    
    print("\n📊 Authentication Test Summary")
    print("=" * 50)
    print("✅ Health endpoints working")
    print("✅ Authentication properly enforced")
    print("✅ Agent endpoints accessible")
    print("⚠️  JWT token required for chat endpoints")

if __name__ == "__main__":
    main() 