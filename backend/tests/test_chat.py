#!/usr/bin/env python3
"""
Chat System Test Script
Tests all chat functionality including sessions and messages
"""

import requests
import json
import time
from typing import Dict, List, Optional

class ChatTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = {
            "username": "testuser_chat",
            "email": "testuser_chat@example.com",
            "password": "TestPass123"
        }
        self.test_sessions = []
        self.test_messages = []

    def setup(self):
        """Setup test environment"""
        print("🔧 Setting up chat test environment...")
        
        # Create test user
        self.create_test_user()
        
        # Login to get auth token
        self.login()
        
        print("✅ Setup complete!")

    def create_test_user(self):
        """Create a test user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user
            )
            if response.status_code == 201:
                print("✅ Test user created successfully")
            elif response.status_code == 409:
                print("ℹ️ Test user already exists")
            else:
                print(f"⚠️ User creation returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating test user: {e}")

    def login(self):
        """Login and get auth token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": self.test_user["username"],
                    "password": self.test_user["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('tokens', {}).get('access_token')
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error during login: {e}")

    def test_session_creation(self):
        """Test chat session creation"""
        print("\n📝 Testing session creation...")
        
        test_sessions = [
            "Test Chat Session 1",
            "AI Discussion",
            "Project Planning",
            "General Chat"
        ]
        
        for title in test_sessions:
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/sessions",
                    json={"title": title}
                )
                
                if response.status_code == 201:
                    session_data = response.json()
                    self.test_sessions.append(session_data['session'])
                    print(f"✅ Created session: {title} (ID: {session_data['session']['id']})")
                else:
                    print(f"❌ Failed to create session '{title}': {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error creating session '{title}': {e}")

    def test_session_retrieval(self):
        """Test getting chat sessions"""
        print("\n📥 Testing session retrieval...")
        
        try:
            response = self.session.get(f"{self.base_url}/chat/sessions")
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get('sessions', [])
                pagination = data.get('pagination', {})
                
                print(f"✅ Retrieved {len(sessions)} sessions")
                print(f"📊 Pagination: Page {pagination.get('page', 1)} of {pagination.get('pages', 1)}")
                
                # Display first few sessions
                for i, session in enumerate(sessions[:3]):
                    print(f"   Session {i+1}: {session['title']} (ID: {session['id']})")
            else:
                print(f"❌ Failed to retrieve sessions: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error retrieving sessions: {e}")

    def test_message_sending(self):
        """Test message sending functionality"""
        print("\n💬 Testing message sending...")
        
        if not self.test_sessions:
            print("⚠️ No test sessions available")
            return
        
        session = self.test_sessions[0]
        test_messages = [
            {"text": "Hello, this is a test message!", "sender": "user"},
            {"text": "How are you doing today?", "sender": "user"},
            {"text": "This is an AI response to your message.", "sender": "ai"},
            {"text": "I'm here to help with any questions you have.", "sender": "ai"},
            {"text": "Let's discuss the project requirements.", "sender": "user"}
        ]
        
        for i, msg in enumerate(test_messages):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/sessions/{session['id']}/messages",
                    json=msg
                )
                
                if response.status_code == 201:
                    message_data = response.json()
                    self.test_messages.append(message_data['message_data'])
                    print(f"✅ Sent message {i+1}: {msg['text'][:30]}...")
                else:
                    print(f"❌ Failed to send message {i+1}: {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error sending message {i+1}: {e}")

    def test_message_retrieval(self):
        """Test message retrieval with pagination"""
        print("\n📥 Testing message retrieval...")
        
        if not self.test_sessions:
            print("⚠️ No test sessions available")
            return
        
        session = self.test_sessions[0]
        
        try:
            response = self.session.get(
                f"{self.base_url}/chat/sessions/{session['id']}/messages"
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                pagination = data.get('pagination', {})
                
                print(f"✅ Retrieved {len(messages)} messages")
                print(f"📊 Pagination: Page {pagination.get('page', 1)} of {pagination.get('pages', 1)}")
                
                # Display first few messages
                for i, msg in enumerate(messages[:3]):
                    print(f"   Message {i+1}: {msg['sender']} - {msg['text'][:50]}...")
            else:
                print(f"❌ Failed to retrieve messages: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error retrieving messages: {e}")

    def test_session_update(self):
        """Test session title update"""
        print("\n✏️ Testing session updates...")
        
        if not self.test_sessions:
            print("⚠️ No test sessions available")
            return
        
        session = self.test_sessions[0]
        
        try:
            new_title = "Updated Session Title"
            response = self.session.put(
                f"{self.base_url}/chat/sessions/{session['id']}",
                json={"title": new_title}
            )
            
            if response.status_code == 200:
                updated_data = response.json()
                print(f"✅ Updated session title to: {new_title}")
            else:
                print(f"❌ Failed to update session: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error updating session: {e}")

    def test_message_update(self):
        """Test message updating"""
        print("\n✏️ Testing message updates...")
        
        if not self.test_messages:
            print("⚠️ No test messages available")
            return
        
        message = self.test_messages[0]
        session_id = message['session_id']
        
        try:
            updated_text = "This message has been updated for testing purposes!"
            response = self.session.put(
                f"{self.base_url}/chat/sessions/{session_id}/messages/{message['id']}",
                json={"text": updated_text}
            )
            
            if response.status_code == 200:
                updated_data = response.json()
                print(f"✅ Updated message: {updated_data['message_data']['text'][:50]}...")
            else:
                print(f"❌ Failed to update message: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error updating message: {e}")

    def test_message_deletion(self):
        """Test message deletion"""
        print("\n🗑️ Testing message deletion...")
        
        if not self.test_messages:
            print("⚠️ No test messages available")
            return
        
        message = self.test_messages[-1]  # Delete last message
        session_id = message['session_id']
        
        try:
            response = self.session.delete(
                f"{self.base_url}/chat/sessions/{session_id}/messages/{message['id']}"
            )
            
            if response.status_code == 200:
                print("✅ Message deleted successfully")
            else:
                print(f"❌ Failed to delete message: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error deleting message: {e}")

    def test_session_deletion(self):
        """Test session deletion"""
        print("\n🗑️ Testing session deletion...")
        
        if not self.test_sessions:
            print("⚠️ No test sessions available")
            return
        
        session = self.test_sessions[-1]  # Delete last session
        
        try:
            response = self.session.delete(
                f"{self.base_url}/chat/sessions/{session['id']}"
            )
            
            if response.status_code == 200:
                print("✅ Session deleted successfully")
            else:
                print(f"❌ Failed to delete session: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error deleting session: {e}")

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚨 Testing error handling...")
        
        # Test invalid session ID
        try:
            response = self.session.get(f"{self.base_url}/chat/sessions/99999")
            if response.status_code == 404:
                print("✅ Correctly handled invalid session ID")
            else:
                print(f"⚠️ Unexpected response for invalid session: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing invalid session: {e}")
        
        # Test invalid message ID
        if self.test_sessions:
            session = self.test_sessions[0]
            try:
                response = self.session.get(f"{self.base_url}/chat/sessions/{session['id']}/messages/99999")
                if response.status_code == 404:
                    print("✅ Correctly handled invalid message ID")
                else:
                    print(f"⚠️ Unexpected response for invalid message: {response.status_code}")
            except Exception as e:
                print(f"❌ Error testing invalid message: {e}")
        
        # Test empty message
        if self.test_sessions:
            session = self.test_sessions[0]
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/sessions/{session['id']}/messages",
                    json={"text": "", "sender": "user"}
                )
                if response.status_code == 400:
                    print("✅ Correctly handled empty message")
                else:
                    print(f"⚠️ Unexpected response for empty message: {response.status_code}")
            except Exception as e:
                print(f"❌ Error testing empty message: {e}")

    def test_performance(self):
        """Test performance with multiple messages"""
        print("\n⚡ Testing performance...")
        
        if not self.test_sessions:
            print("⚠️ No test sessions available")
            return
        
        session = self.test_sessions[0]
        start_time = time.time()
        
        # Send multiple messages quickly
        for i in range(10):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/sessions/{session['id']}/messages",
                    json={
                        "text": f"Performance test message {i+1}",
                        "sender": "user"
                    }
                )
                
                if response.status_code != 201:
                    print(f"❌ Failed to send performance test message {i+1}")
            except Exception as e:
                print(f"❌ Error in performance test message {i+1}: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Sent 10 messages in {duration:.2f} seconds")
        print(f"📊 Average: {duration/10:.3f} seconds per message")

    def run_all_tests(self):
        """Run all chat tests"""
        print("🚀 Starting Chat System Tests")
        print("=" * 50)
        
        try:
            self.setup()
            self.test_session_creation()
            self.test_session_retrieval()
            self.test_message_sending()
            self.test_message_retrieval()
            self.test_session_update()
            self.test_message_update()
            self.test_message_deletion()
            self.test_session_deletion()
            self.test_error_handling()
            self.test_performance()
            
            print("\n" + "=" * 50)
            print("✅ All chat system tests completed!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    tester = ChatTester()
    tester.run_all_tests() 