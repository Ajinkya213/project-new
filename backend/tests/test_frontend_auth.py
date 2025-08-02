#!/usr/bin/env python3
"""
Test frontend authentication flow
"""

import requests
import json

def test_login():
    """Test login endpoint"""
    print("🔐 Testing Login")
    print("=" * 50)
    
    # Test login with test credentials
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
            print(f"📄 Full response: {result}")
            access_token = result.get('access_token') or result.get('tokens', {}).get('access_token')
            print(f"📄 Access token: {access_token[:20] if access_token else 'NOT_FOUND'}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_chat_with_token(token):
    """Test chat endpoints with valid token"""
    print("\n💬 Testing Chat with Token")
    print("=" * 50)
    
    if not token:
        print("❌ No token available")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get sessions
    print("\n📋 Testing Get Sessions")
    try:
        response = requests.get("http://localhost:8000/chat/sessions", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Get sessions successful")
            print(f"📊 Sessions found: {len(result.get('sessions', []))}")
        else:
            print(f"❌ Get sessions failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Get sessions error: {e}")
    
    # Test 2: Create session
    print("\n➕ Testing Create Session")
    try:
        session_data = {"title": "Test Session"}
        response = requests.post("http://localhost:8000/chat/sessions", json=session_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print("✅ Create session successful")
            session_id = result.get('session', {}).get('id')
            print(f"📄 Session ID: {session_id}")
            return session_id
        else:
            print(f"❌ Create session failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Create session error: {e}")
        return None

def test_send_message(token, session_id):
    """Test sending a message"""
    print("\n💬 Testing Send Message")
    print("=" * 50)
    
    if not token or not session_id:
        print("❌ Missing token or session ID")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test user message
    print("\n👤 Testing User Message")
    try:
        message_data = {
            "text": "Hello, this is a test message",
            "sender": "user"
        }
        response = requests.post(
            f"http://localhost:8000/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=headers
        )
        if response.status_code == 201:
            result = response.json()
            print("✅ User message sent successfully")
            message_id = result.get('message_data', {}).get('id')
            print(f"📄 Message ID: {message_id}")
            return message_id
        else:
            print(f"❌ User message failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User message error: {e}")
        return None

def test_ai_message(token, session_id):
    """Test sending an AI message"""
    print("\n🤖 Testing AI Message")
    print("=" * 50)
    
    if not token or not session_id:
        print("❌ Missing token or session ID")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        message_data = {
            "text": "Hello! I'm an AI assistant. How can I help you today?",
            "sender": "ai",
            "agent_info": {
                "selectedAgent": "chat",
                "confidence": 0.95
            }
        }
        response = requests.post(
            f"http://localhost:8000/chat/sessions/{session_id}/messages",
            json=message_data,
            headers=headers
        )
        if response.status_code == 201:
            result = response.json()
            print("✅ AI message sent successfully")
            message_id = result.get('message_data', {}).get('id')
            print(f"📄 Message ID: {message_id}")
            return message_id
        else:
            print(f"❌ AI message failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ AI message error: {e}")
        return None

def main():
    """Main test function"""
    print("🔐 Frontend Authentication Test")
    print("=" * 50)
    
    # Test 1: Login
    token = test_login()
    
    if token:
        # Test 2: Create session
        session_id = test_chat_with_token(token)
        
        if session_id:
            # Test 3: Send user message
            user_message_id = test_send_message(token, session_id)
            
            # Test 4: Send AI message
            ai_message_id = test_ai_message(token, session_id)
            
            print("\n📊 Frontend Auth Test Summary")
            print("=" * 50)
            print(f"Login: {'✅' if token else '❌'}")
            print(f"Session Creation: {'✅' if session_id else '❌'}")
            print(f"User Message: {'✅' if user_message_id else '❌'}")
            print(f"AI Message: {'✅' if ai_message_id else '❌'}")
            
            if token and session_id and user_message_id and ai_message_id:
                print("\n🎉 All frontend authentication tests passed!")
            else:
                print("\n⚠️  Some tests failed. Check the issues above.")
        else:
            print("\n❌ Session creation failed")
    else:
        print("\n❌ Login failed")

if __name__ == "__main__":
    main() 