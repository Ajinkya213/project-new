#!/usr/bin/env python3
"""
Test script to simulate frontend behavior and verify user isolation
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'

def test_frontend_isolation():
    """Test that users are properly isolated when logging in and out"""
    
    print("Testing frontend user isolation...")
    
    # Test data
    user1_data = {
        'username': 'frontenduser1',
        'email': 'frontenduser1@example.com',
        'password': 'TestPass123!'
    }
    
    user2_data = {
        'username': 'frontenduser2',
        'email': 'frontenduser2@example.com',
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
    
    # Step 3: User1 creates sessions and sends messages
    print("\n3. User1 creating sessions and sending messages...")
    headers1 = {'Authorization': f'Bearer {user1_tokens["access_token"]}'}
    
    # Create session 1
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'User1 Session 1'}, 
                           headers=headers1)
    if response.status_code == 201:
        user1_session1 = response.json()['session']
        print(f"✓ User1 session 1 created: {user1_session1['id']}")
    else:
        print(f"✗ User1 session 1 creation failed: {response.json()}")
        return
    
    # Send message to session 1
    response = requests.post(f'{BASE_URL}/chat/sessions/{user1_session1["id"]}/messages',
                           json={'text': 'Hello from User1 Session 1', 'sender': 'user'},
                           headers=headers1)
    if response.status_code == 201:
        print("✓ User1 message sent to session 1")
    else:
        print(f"✗ User1 message failed: {response.json()}")
        return
    
    # Create session 2
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'User1 Session 2'}, 
                           headers=headers1)
    if response.status_code == 201:
        user1_session2 = response.json()['session']
        print(f"✓ User1 session 2 created: {user1_session2['id']}")
    else:
        print(f"✗ User1 session 2 creation failed: {response.json()}")
        return
    
    # Send message to session 2
    response = requests.post(f'{BASE_URL}/chat/sessions/{user1_session2["id"]}/messages',
                           json={'text': 'Hello from User1 Session 2', 'sender': 'user'},
                           headers=headers1)
    if response.status_code == 201:
        print("✓ User1 message sent to session 2")
    else:
        print(f"✗ User1 message failed: {response.json()}")
        return
    
    # Step 4: User1 gets their sessions (should see 2 sessions)
    print("\n4. User1 getting their sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers1)
    if response.status_code == 200:
        user1_sessions = response.json()['sessions']
        print(f"✓ User1 has {len(user1_sessions)} sessions")
        for session in user1_sessions:
            print(f"  - Session {session['id']}: {session['title']}")
        
        if len(user1_sessions) != 2:
            print(f"✗ Expected 2 sessions, got {len(user1_sessions)}")
            return
    else:
        print(f"✗ User1 sessions fetch failed: {response.json()}")
        return
    
    # Step 5: User1 logs out (simulate frontend logout)
    print("\n5. User1 logging out...")
    response = requests.post(f'{BASE_URL}/auth/logout', headers=headers1)
    if response.status_code == 200:
        print("✓ User1 logged out successfully")
    else:
        print(f"✗ User1 logout failed: {response.json()}")
        return
    
    # Step 6: User2 logs in and creates sessions
    print("\n6. User2 creating sessions and sending messages...")
    headers2 = {'Authorization': f'Bearer {user2_tokens["access_token"]}'}
    
    # Create session for user2
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'User2 Session'}, 
                           headers=headers2)
    if response.status_code == 201:
        user2_session = response.json()['session']
        print(f"✓ User2 session created: {user2_session['id']}")
    else:
        print(f"✗ User2 session creation failed: {response.json()}")
        return
    
    # Send message to user2 session
    response = requests.post(f'{BASE_URL}/chat/sessions/{user2_session["id"]}/messages',
                           json={'text': 'Hello from User2', 'sender': 'user'},
                           headers=headers2)
    if response.status_code == 201:
        print("✓ User2 message sent successfully")
    else:
        print(f"✗ User2 message failed: {response.json()}")
        return
    
    # Step 7: User2 gets their sessions (should see only 1 session)
    print("\n7. User2 getting their sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers2)
    if response.status_code == 200:
        user2_sessions = response.json()['sessions']
        print(f"✓ User2 has {len(user2_sessions)} sessions")
        for session in user2_sessions:
            print(f"  - Session {session['id']}: {session['title']}")
        
        if len(user2_sessions) != 1:
            print(f"✗ Expected 1 session, got {len(user2_sessions)}")
            return
    else:
        print(f"✗ User2 sessions fetch failed: {response.json()}")
        return
    
    # Step 8: Verify User2 cannot see User1's sessions
    print("\n8. Verifying User2 cannot access User1's sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{user1_session1["id"]}', headers=headers2)
    if response.status_code == 403:
        print("✓ User2 correctly denied access to User1's session 1")
    else:
        print(f"✗ Security issue: User2 can access User1's session 1: {response.status_code}")
        return
    
    response = requests.get(f'{BASE_URL}/chat/sessions/{user1_session2["id"]}', headers=headers2)
    if response.status_code == 403:
        print("✓ User2 correctly denied access to User1's session 2")
    else:
        print(f"✗ Security issue: User2 can access User1's session 2: {response.status_code}")
        return
    
    # Step 9: User1 logs back in and should only see their own sessions
    print("\n9. User1 logging back in...")
    response = requests.post(f'{BASE_URL}/auth/login', json=user1_data)
    if response.status_code == 200:
        user1_new_tokens = response.json()['tokens']
        print("✓ User1 logged back in successfully")
    else:
        print(f"✗ User1 login failed: {response.json()}")
        return
    
    headers1_new = {'Authorization': f'Bearer {user1_new_tokens["access_token"]}'}
    
    # User1 gets their sessions again
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers1_new)
    if response.status_code == 200:
        user1_sessions_after_login = response.json()['sessions']
        print(f"✓ User1 has {len(user1_sessions_after_login)} sessions after logging back in")
        for session in user1_sessions_after_login:
            print(f"  - Session {session['id']}: {session['title']}")
        
        if len(user1_sessions_after_login) != 2:
            print(f"✗ Expected 2 sessions, got {len(user1_sessions_after_login)}")
            return
    else:
        print(f"✗ User1 sessions fetch failed: {response.json()}")
        return
    
    print("\n🎉 All frontend isolation tests passed! Users are properly isolated even after logout/login cycles.")

if __name__ == '__main__':
    test_frontend_isolation() 