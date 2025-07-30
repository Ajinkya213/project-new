#!/usr/bin/env python3
"""
Test script to verify user isolation in chat sessions
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_user_isolation():
    """Test that users can only see their own chat sessions"""
    
    print("Testing user isolation...")
    
    # Test data
    user1_data = {
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'password': 'TestPass123!'
    }
    
    user2_data = {
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'password': 'TestPass123!'
    }
    
    # Step 1: Register user1
    print("\n1. Registering user1...")
    response = requests.post(f'{BASE_URL}/auth/register', json=user1_data)
    if response.status_code == 201:
        user1_tokens = response.json()['tokens']
        print("✓ User1 registered successfully")
    else:
        print(f"✗ User1 registration failed: {response.json()}")
        return
    
    # Step 2: Register user2
    print("\n2. Registering user2...")
    response = requests.post(f'{BASE_URL}/auth/register', json=user2_data)
    if response.status_code == 201:
        user2_tokens = response.json()['tokens']
        print("✓ User2 registered successfully")
    else:
        print(f"✗ User2 registration failed: {response.json()}")
        return
    
    # Step 3: User1 creates a chat session
    print("\n3. User1 creating chat session...")
    headers1 = {'Authorization': f'Bearer {user1_tokens["access_token"]}'}
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'User1 Session'}, 
                           headers=headers1)
    if response.status_code == 201:
        user1_session = response.json()['session']
        print(f"✓ User1 session created: {user1_session['id']}")
    else:
        print(f"✗ User1 session creation failed: {response.json()}")
        return
    
    # Step 4: User2 creates a chat session
    print("\n4. User2 creating chat session...")
    headers2 = {'Authorization': f'Bearer {user2_tokens["access_token"]}'}
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'User2 Session'}, 
                           headers=headers2)
    if response.status_code == 201:
        user2_session = response.json()['session']
        print(f"✓ User2 session created: {user2_session['id']}")
    else:
        print(f"✗ User2 session creation failed: {response.json()}")
        return
    
    # Step 5: User1 sends a message
    print("\n5. User1 sending message...")
    response = requests.post(f'{BASE_URL}/chat/sessions/{user1_session["id"]}/messages',
                           json={'text': 'Hello from User1', 'sender': 'user'},
                           headers=headers1)
    if response.status_code == 201:
        print("✓ User1 message sent successfully")
    else:
        print(f"✗ User1 message failed: {response.json()}")
        return
    
    # Step 6: User2 sends a message
    print("\n6. User2 sending message...")
    response = requests.post(f'{BASE_URL}/chat/sessions/{user2_session["id"]}/messages',
                           json={'text': 'Hello from User2', 'sender': 'user'},
                           headers=headers2)
    if response.status_code == 201:
        print("✓ User2 message sent successfully")
    else:
        print(f"✗ User2 message failed: {response.json()}")
        return
    
    # Step 7: User1 gets their sessions
    print("\n7. User1 getting their sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers1)
    if response.status_code == 200:
        user1_sessions = response.json()['sessions']
        print(f"✓ User1 has {len(user1_sessions)} sessions")
        for session in user1_sessions:
            print(f"  - Session {session['id']}: {session['title']}")
    else:
        print(f"✗ User1 sessions fetch failed: {response.json()}")
        return
    
    # Step 8: User2 gets their sessions
    print("\n8. User2 getting their sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers2)
    if response.status_code == 200:
        user2_sessions = response.json()['sessions']
        print(f"✓ User2 has {len(user2_sessions)} sessions")
        for session in user2_sessions:
            print(f"  - Session {session['id']}: {session['title']}")
    else:
        print(f"✗ User2 sessions fetch failed: {response.json()}")
        return
    
    # Step 9: Test isolation - User1 tries to access User2's session
    print("\n9. Testing isolation - User1 trying to access User2's session...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{user2_session["id"]}', headers=headers1)
    if response.status_code == 403:
        print("✓ User1 correctly denied access to User2's session")
    else:
        print(f"✗ Security issue: User1 can access User2's session: {response.status_code}")
        return
    
    # Step 10: Test isolation - User2 tries to access User1's session
    print("\n10. Testing isolation - User2 trying to access User1's session...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{user1_session["id"]}', headers=headers2)
    if response.status_code == 403:
        print("✓ User2 correctly denied access to User1's session")
    else:
        print(f"✗ Security issue: User2 can access User1's session: {response.status_code}")
        return
    
    print("\n🎉 All isolation tests passed! Users are properly isolated.")

if __name__ == '__main__':
    test_user_isolation() 