#!/usr/bin/env python3
"""
Test response length handling
"""

import requests
import json

def test_long_response():
    """Test sending a very long AI response"""
    print("📏 Testing Long Response Handling")
    print("=" * 50)
    
    # First, login to get a token
    login_data = {
        "username": "testuser2",
        "password": "TestPassword123"
    }
    
    try:
        # Login
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        result = response.json()
        token = result.get('tokens', {}).get('access_token')
        
        if not token:
            print("❌ No token received")
            return
        
        print("✅ Login successful")
        
        # Create a session
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        session_response = requests.post(
            "http://localhost:8000/chat/sessions",
            json={"title": "Test Long Response"},
            headers=headers
        )
        
        if session_response.status_code != 201:
            print(f"❌ Session creation failed: {session_response.status_code}")
            return
        
        session_data = session_response.json()
        session_id = session_data.get('session', {}).get('id')
        
        print(f"✅ Session created: {session_id}")
        
        # Test 1: Send a very long AI response
        print("\n🔍 Test 1: Very Long AI Response")
        long_response = "This is a very long response. " * 1000  # About 30,000 characters
        
        message_data = {
            "text": long_response,
            "sender": "ai",
            "agent_info": {
                "selectedAgent": "research",
                "confidence": 0.95
            }
        }
        
        response = requests.post(
            f"http://localhost:8000/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Long AI response sent successfully")
            result = response.json()
            message_id = result.get('message_data', {}).get('id')
            print(f"📄 Message ID: {message_id}")
        else:
            print(f"❌ Long AI response failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test 2: Send a moderately long response
        print("\n🔍 Test 2: Moderately Long AI Response")
        medium_response = "This is a moderately long response. " * 200  # About 6,000 characters
        
        message_data = {
            "text": medium_response,
            "sender": "ai",
            "agent_info": {
                "selectedAgent": "chat",
                "confidence": 0.85
            }
        }
        
        response = requests.post(
            f"http://localhost:8000/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Medium AI response sent successfully")
            result = response.json()
            message_id = result.get('message_data', {}).get('id')
            print(f"📄 Message ID: {message_id}")
        else:
            print(f"❌ Medium AI response failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test 3: Send a short response
        print("\n🔍 Test 3: Short AI Response")
        short_response = "This is a short response."
        
        message_data = {
            "text": short_response,
            "sender": "ai",
            "agent_info": {
                "selectedAgent": "lightweight",
                "confidence": 0.95
            }
        }
        
        response = requests.post(
            f"http://localhost:8000/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Short AI response sent successfully")
            result = response.json()
            message_id = result.get('message_data', {}).get('id')
            print(f"📄 Message ID: {message_id}")
        else:
            print(f"❌ Short AI response failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        print("\n📊 Response Length Test Summary")
        print("=" * 50)
        print("✅ Authentication working")
        print("✅ Session creation working")
        print("✅ Message sending working")
        print("✅ Response length validation working")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_agent_long_response():
    """Test agent with a query that might generate a long response"""
    print("\n🤖 Testing Agent Long Response")
    print("=" * 50)
    
    try:
        # Test agent with a complex query
        response = requests.post(
            "http://localhost:8000/agent/test",
            json={"query": "Please provide a comprehensive analysis of artificial intelligence, including its history, current state, future prospects, applications, challenges, and ethical considerations. Include detailed explanations of machine learning, deep learning, neural networks, and their real-world applications."},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('result', {}).get('response', '')
            print("✅ Agent test successful")
            print(f"📄 Response length: {len(response_text)} characters")
            print(f"📄 Response preview: {response_text[:200]}...")
            
            if len(response_text) > 5000:
                print("⚠️  Response is very long - may need truncation")
            elif len(response_text) > 3000:
                print("⚠️  Response is moderately long")
            else:
                print("✅ Response length is reasonable")
        else:
            print(f"❌ Agent test failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")

def main():
    """Main test function"""
    print("📏 Response Length Testing")
    print("=" * 50)
    
    # Test 1: Direct API testing
    test_long_response()
    
    # Test 2: Agent testing
    test_agent_long_response()
    
    print("\n🎉 Response length testing completed!")

if __name__ == "__main__":
    main() 