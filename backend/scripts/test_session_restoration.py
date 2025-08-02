#!/usr/bin/env python3
"""
Test script to verify session restoration when users log back in
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'

def test_session_restoration():
    """Test that user sessions are properly restored when logging back in"""
    
    print("Testing session restoration...")
    
    # Test data
    user_data = {
        'username': 'restoreuser',
        'email': 'restoreuser@example.com',
        'password': 'TestPass123!'
    }
    
    # Step 1: Register user
    print("\n1. Registering user...")
    response = requests.post(f'{BASE_URL}/auth/register', json=user_data)
    if response.status_code == 201:
        tokens = response.json()['tokens']
        print("✓ User registered successfully")
    else:
        print(f"✗ User registration failed: {response.json()}")
        return
    
    # Step 2: User creates multiple sessions and sends messages
    print("\n2. User creating sessions and sending messages...")
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    
    # Create session 1
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'Restore Session 1'}, 
                           headers=headers)
    if response.status_code == 201:
        session1 = response.json()['session']
        print(f"✓ Session 1 created: {session1['id']}")
    else:
        print(f"✗ Session 1 creation failed: {response.json()}")
        return
    
    # Send messages to session 1
    for i in range(3):
        response = requests.post(f'{BASE_URL}/chat/sessions/{session1["id"]}/messages',
                               json={'text': f'Message {i+1} from Session 1', 'sender': 'user'},
                               headers=headers)
        if response.status_code == 201:
            print(f"✓ Message {i+1} sent to Session 1")
        else:
            print(f"✗ Message {i+1} failed: {response.json()}")
            return
    
    # Create session 2
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'Restore Session 2'}, 
                           headers=headers)
    if response.status_code == 201:
        session2 = response.json()['session']
        print(f"✓ Session 2 created: {session2['id']}")
    else:
        print(f"✗ Session 2 creation failed: {response.json()}")
        return
    
    # Send messages to session 2
    for i in range(2):
        response = requests.post(f'{BASE_URL}/chat/sessions/{session2["id"]}/messages',
                               json={'text': f'Message {i+1} from Session 2', 'sender': 'user'},
                               headers=headers)
        if response.status_code == 201:
            print(f"✓ Message {i+1} sent to Session 2")
        else:
            print(f"✗ Message {i+1} failed: {response.json()}")
            return
    
    # Step 3: User gets their sessions (should see 2 sessions)
    print("\n3. User getting their sessions...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers)
    if response.status_code == 200:
        sessions = response.json()['sessions']
        print(f"✓ User has {len(sessions)} sessions")
        for session in sessions:
            print(f"  - Session {session['id']}: {session['title']}")
        
        if len(sessions) != 2:
            print(f"✗ Expected 2 sessions, got {len(sessions)}")
            return
    else:
        print(f"✗ Sessions fetch failed: {response.json()}")
        return
    
    # Step 4: User logs out
    print("\n4. User logging out...")
    response = requests.post(f'{BASE_URL}/auth/logout', headers=headers)
    if response.status_code == 200:
        print("✓ User logged out successfully")
    else:
        print(f"✗ User logout failed: {response.json()}")
        return
    
    # Step 5: User logs back in
    print("\n5. User logging back in...")
    response = requests.post(f'{BASE_URL}/auth/login', json=user_data)
    if response.status_code == 200:
        new_tokens = response.json()['tokens']
        print("✓ User logged back in successfully")
    else:
        print(f"✗ User login failed: {response.json()}")
        return
    
    # Step 6: User gets their sessions again (should see the same 2 sessions)
    print("\n6. User getting their sessions after login...")
    new_headers = {'Authorization': f'Bearer {new_tokens["access_token"]}'}
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=new_headers)
    if response.status_code == 200:
        restored_sessions = response.json()['sessions']
        print(f"✓ User has {len(restored_sessions)} sessions after login")
        for session in restored_sessions:
            print(f"  - Session {session['id']}: {session['title']}")
        
        if len(restored_sessions) != 2:
            print(f"✗ Expected 2 sessions, got {len(restored_sessions)}")
            return
    else:
        print(f"✗ Sessions fetch failed: {response.json()}")
        return
    
    # Step 7: Verify session IDs are the same (sessions were restored, not recreated)
    print("\n7. Verifying session restoration...")
    original_session_ids = [session['id'] for session in sessions]
    restored_session_ids = [session['id'] for session in restored_sessions]
    
    if set(original_session_ids) == set(restored_session_ids):
        print("✓ Session IDs match - sessions were properly restored")
    else:
        print("✗ Session IDs don't match - sessions were recreated instead of restored")
        print(f"  Original: {original_session_ids}")
        print(f"  Restored: {restored_session_ids}")
        return
    
    # Step 8: Verify messages are still there by getting a specific session
    print("\n8. Verifying messages are preserved...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{session1["id"]}', headers=new_headers)
    if response.status_code == 200:
        session_data = response.json()['session']
        message_count = len(session_data['messages'])
        print(f"✓ Session 1 has {message_count} messages")
        
        if message_count >= 3:  # Should have at least 3 user messages
            print("✓ Messages were properly preserved")
        else:
            print(f"✗ Expected at least 3 messages, got {message_count}")
            return
    else:
        print(f"✗ Failed to get session details: {response.json()}")
        return
    
    print("\n🎉 All session restoration tests passed! Sessions are properly restored when users log back in.")

if __name__ == '__main__':
    test_session_restoration() 