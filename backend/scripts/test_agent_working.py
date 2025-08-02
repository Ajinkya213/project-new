#!/usr/bin/env python3
"""
Test to verify agent is working properly
"""

import requests
import json

def test_agent_comprehensive():
    """Comprehensive test of agent functionality"""
    base_url = "http://localhost:8000"
    
    print("🤖 Comprehensive Agent Test")
    print("=" * 50)
    
    # Test 1: Agent Health
    print("\n1. Testing Agent Health...")
    try:
        response = requests.get(f"{base_url}/agent/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Health Check:")
            print(f"   - Status: {data.get('status', 'unknown')}")
            print(f"   - Available Agents: {len(data.get('available_agents', {}))}")
            print(f"   - Query Service: {data.get('query_service', {}).get('status', 'unknown')}")
            print(f"   - Lightweight Agent: {data.get('lightweight_agent', {}).get('status', 'unknown')}")
        else:
            print("❌ Agent health check failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Agent Test Endpoint
    print("\n2. Testing Agent Test Endpoint...")
    try:
        response = requests.post(
            f"{base_url}/agent/test",
            json={"query": "Hello, how are you?"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Test Response:")
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Response: {data.get('result', {}).get('response', 'No response')}")
        else:
            print("❌ Agent test failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Authenticated Agent Query
    print("\n3. Testing Authenticated Agent Query...")
    try:
        # First login
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            tokens = login_response.json()["tokens"]
            access_token = tokens["access_token"]
            
            # Test agent query
            query_response = requests.post(
                f"{base_url}/agent/query",
                json={
                    "query": "What is artificial intelligence?",
                    "agent_type": "lightweight"
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            print(f"Status: {query_response.status_code}")
            if query_response.status_code == 200:
                data = query_response.json()
                print("✅ Authenticated Agent Query:")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Agent Type: {data.get('agent_type', 'unknown')}")
                print(f"   - Response: {data.get('response', 'No response')[:100]}...")
            else:
                print("❌ Authenticated agent query failed")
        else:
            print("❌ Login failed for authenticated test")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Different Agent Types
    print("\n4. Testing Different Agent Types...")
    try:
        if login_response.status_code == 200:
            tokens = login_response.json()["tokens"]
            access_token = tokens["access_token"]
            
            agent_types = ["lightweight", "chat", "document", "research"]
            
            for agent_type in agent_types:
                try:
                    response = requests.post(
                        f"{base_url}/agent/query",
                        json={
                            "query": "Hello",
                            "agent_type": agent_type
                        },
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {access_token}"
                        }
                    )
                    
                    print(f"   {agent_type}: Status {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"     ✅ Success: {data.get('success', False)}")
                    else:
                        print(f"     ❌ Failed")
                        
                except Exception as e:
                    print(f"     ❌ Error: {e}")
        else:
            print("❌ Cannot test agent types - login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_agent_comprehensive() 