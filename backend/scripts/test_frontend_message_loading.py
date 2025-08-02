#!/usr/bin/env python3
"""
Test script to simulate frontend message loading behavior
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'

def test_frontend_message_loading():
    """Test that simulates frontend message loading behavior"""
    
    print("Testing frontend message loading simulation...")
    
    # Test data
    user_data = {
        'username': 'frontendtest',
        'email': 'frontendtest@example.com',
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
                           json={'title': 'Frontend Test Session'}, 
                           headers=headers)
    if response.status_code == 201:
        session = response.json()['session']
        print(f"✓ Session created: {session['id']}")
    else:
        print(f"✗ Session creation failed: {response.json()}")
        return
    
    # Send messages
    messages = [
        "Frontend test message 1",
        "Frontend test message 2",
        "Frontend test message 3"
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
    
    # Step 3: Simulate frontend session loading (like loadSessions)
    print("\n3. Simulating frontend session loading...")
    
    # First, get sessions (like frontend loadSessions)
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers)
    if response.status_code == 200:
        sessions_data = response.json()['sessions']
        print(f"✓ Got {len(sessions_data)} sessions")
        
        for session_data in sessions_data:
            session_id = session_data['id']
            print(f"  - Session {session_id}: {session_data['title']}")
            
            # Simulate loading messages for each session (like frontend loadMessages)
            print(f"    Loading messages for session {session_id}...")
            response = requests.get(f'{BASE_URL}/chat/sessions/{session_id}/messages', headers=headers)
            if response.status_code == 200:
                messages_data = response.json()['messages']
                print(f"    ✓ Loaded {len(messages_data)} messages for session {session_id}")
                for msg in messages_data:
                    print(f"      - Message: {msg['text']}")
            else:
                print(f"    ✗ Failed to load messages for session {session_id}: {response.json()}")
    else:
        print(f"✗ Failed to get sessions: {response.json()}")
        return
    
    # Step 4: Simulate multiple session loads (like frontend periodic reloads)
    print("\n4. Simulating multiple session loads (like frontend periodic reloads)...")
    
    for i in range(3):
        print(f"\n  Load attempt {i+1}:")
        
        # Get sessions again
        response = requests.get(f'{BASE_URL}/chat/sessions', headers=headers)
        if response.status_code == 200:
            sessions_data = response.json()['sessions']
            print(f"  ✓ Got {len(sessions_data)} sessions")
            
            for session_data in sessions_data:
                session_id = session_data['id']
                
                # Load messages for each session
                response = requests.get(f'{BASE_URL}/chat/sessions/{session_id}/messages', headers=headers)
                if response.status_code == 200:
                    messages_data = response.json()['messages']
                    print(f"    ✓ Session {session_id}: {len(messages_data)} messages")
                else:
                    print(f"    ✗ Session {session_id}: Failed to load messages")
        else:
            print(f"  ✗ Failed to get sessions: {response.json()}")
    
    # Step 5: Verify final state
    print("\n5. Verifying final state...")
    response = requests.get(f'{BASE_URL}/chat/sessions/{session["id"]}', headers=headers)
    if response.status_code == 200:
        session_data = response.json()['session']
        final_messages = session_data['messages']
        print(f"✓ Final session has {len(final_messages)} messages")
        
        if len(final_messages) == len(messages):
            print("✓ All messages are still present")
            for i, msg in enumerate(final_messages, 1):
                print(f"  - Message {i}: {msg['text']}")
        else:
            print(f"✗ Expected {len(messages)} messages, got {len(final_messages)}")
            return
    else:
        print(f"✗ Failed to get final session: {response.json()}")
        return
    
    print("\n🎉 Frontend message loading simulation completed successfully!")

if __name__ == '__main__':
    test_frontend_message_loading() 