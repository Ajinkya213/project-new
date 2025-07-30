#!/usr/bin/env python3
"""
Test script to verify message persistence and ensure messages are not being deleted
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'

def test_message_persistence():
    """Test that messages persist correctly and are not deleted"""
    
    print("Testing message persistence...")
    
    # Test data
    user_data = {
        'username': 'messageuser2',
        'email': 'messageuser2@example.com',
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
    
    # Step 2: Create session and send messages
    print("\n2. Creating session and sending messages...")
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    
    # Create session
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'Message Persistence Test'}, 
                           headers=headers)
    if response.status_code == 201:
        session = response.json()['session']
        print(f"✓ Session created: {session['id']}")
    else:
        print(f"✗ Session creation failed: {response.json()}")
        return
    
    # Send multiple messages
    messages = [
        "Hello, this is message 1",
        "This is message 2",
        "And this is message 3",
        "Final message 4"
    ]
    
    for i, message in enumerate(messages, 1):
        response = requests.post(f'{BASE_URL}/chat/sessions/{session["id"]}/messages',
                               json={'text': message, 'sender': 'user'},
                               headers=headers)
        if response.status_code == 201:
            print(f"✓ Message {i} sent: {message}")
        else:
            print(f"✗ Message {i} failed: {response.json()}")
            return
    
    # Step 3: Verify messages are stored
    print("\n3. Verifying messages are stored...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{session["id"]}', headers=headers)
    if response.status_code == 200:
        session_data = response.json()['session']
        stored_messages = session_data['messages']
        print(f"✓ Session has {len(stored_messages)} messages")
        
        if len(stored_messages) == len(messages):
            print("✓ All messages are stored correctly")
            for i, msg in enumerate(stored_messages):
                print(f"  - Message {i+1}: {msg['text']}")
        else:
            print(f"✗ Expected {len(messages)} messages, got {len(stored_messages)}")
            return
    else:
        print(f"✗ Failed to get session: {response.json()}")
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
    
    # Step 6: Verify messages are still there after login
    print("\n6. Verifying messages persist after login...")
    new_headers = {'Authorization': f'Bearer {new_tokens["access_token"]}'}
    response = requests.get(f'{BASE_URL}/chat/sessions/{session["id"]}', headers=new_headers)
    if response.status_code == 200:
        session_data = response.json()['session']
        restored_messages = session_data['messages']
        print(f"✓ Session has {len(restored_messages)} messages after login")
        
        if len(restored_messages) == len(messages):
            print("✓ All messages are still there after login")
            for i, msg in enumerate(restored_messages):
                print(f"  - Message {i+1}: {msg['text']}")
        else:
            print(f"✗ Expected {len(messages)} messages, got {len(restored_messages)}")
            return
    else:
        print(f"✗ Failed to get session after login: {response.json()}")
        return
    
    # Step 7: Send a new message and verify it's added correctly
    print("\n7. Sending new message and verifying...")
    new_message = "This is a new message after login"
    response = requests.post(f'{BASE_URL}/chat/sessions/{session["id"]}/messages',
                           json={'text': new_message, 'sender': 'user'},
                           headers=new_headers)
    if response.status_code == 201:
        print(f"✓ New message sent: {new_message}")
    else:
        print(f"✗ New message failed: {response.json()}")
        return
    
    # Step 8: Verify all messages including the new one
    print("\n8. Verifying all messages including new one...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{session["id"]}', headers=new_headers)
    if response.status_code == 200:
        session_data = response.json()['session']
        all_messages = session_data['messages']
        expected_count = len(messages) + 1  # Original messages + new message
        
        print(f"✓ Session has {len(all_messages)} messages total")
        
        if len(all_messages) == expected_count:
            print("✓ All messages are present including the new one")
            for i, msg in enumerate(all_messages):
                print(f"  - Message {i+1}: {msg['text']}")
        else:
            print(f"✗ Expected {expected_count} messages, got {len(all_messages)}")
            return
    else:
        print(f"✗ Failed to get session: {response.json()}")
        return
    
    print("\n🎉 All message persistence tests passed! Messages are not being deleted.")

if __name__ == '__main__':
    test_message_persistence() 