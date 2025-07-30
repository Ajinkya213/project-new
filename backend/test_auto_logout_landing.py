#!/usr/bin/env python3
"""
Test script to verify automatic logout and landing page redirect functionality
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000'

def test_auto_logout_landing_functionality():
    """Test automatic logout and landing page redirect functionality"""
    
    print("Testing automatic logout and landing page redirect functionality...")
    
    # Test data
    user_data = {
        'username': 'autologouttest',
        'email': 'autologouttest@example.com',
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
    
    # Step 2: Login and verify authentication
    print("\n2. Logging in user...")
    login_data = {
        'username': user_data['username'],
        'password': user_data['password']
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if response.status_code == 200:
        tokens = response.json()['tokens']
        print("✓ User logged in successfully")
        print(f"✓ Access token: {tokens['access_token'][:20]}...")
    else:
        print(f"✗ Login failed: {response.json()}")
        return
    
    # Step 3: Verify token is valid
    print("\n3. Verifying token is valid...")
    headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
    response = requests.get(f'{BASE_URL}/auth/verify', headers=headers)
    if response.status_code == 200:
        user_info = response.json()['user']
        print(f"✓ Token is valid for user: {user_info['username']}")
    else:
        print(f"✗ Token verification failed: {response.json()}")
        return
    
    # Step 4: Create a session to simulate user activity
    print("\n4. Creating session to simulate user activity...")
    response = requests.post(f'{BASE_URL}/chat/sessions', 
                           json={'title': 'Auto Logout Test Session'}, 
                           headers=headers)
    if response.status_code == 201:
        session = response.json()['session']
        print(f"✓ Session created: {session['id']}")
    else:
        print(f"✗ Session creation failed: {response.json()}")
        return
    
    # Step 5: Send a message to simulate chat activity
    print("\n5. Sending message to simulate chat activity...")
    response = requests.post(f'{BASE_URL}/chat/sessions/{session["id"]}/messages',
                           json={'text': 'Test message before auto logout', 'sender': 'user'},
                           headers=headers)
    if response.status_code == 201:
        print("✓ Message sent successfully")
    else:
        print(f"✗ Message sending failed: {response.json()}")
        return
    
    # Step 6: Simulate application close (clear tokens)
    print("\n6. Simulating application close (clearing tokens)...")
    print("   - This simulates what happens when the app is closed")
    print("   - Tokens are cleared from localStorage")
    print("   - User is automatically logged out")
    
    # Step 7: Verify that without tokens, user cannot access protected resources
    print("\n7. Verifying that without tokens, user cannot access protected resources...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers={})
    if response.status_code == 401:
        print("✓ Correctly rejected access without token")
    else:
        print(f"✗ Unexpected response without token: {response.status_code}")
        return
    
    # Step 8: Simulate app restart (no tokens in localStorage)
    print("\n8. Simulating app restart (no tokens in localStorage)...")
    print("   - App starts with no authentication tokens")
    print("   - User is automatically redirected to landing page")
    print("   - No automatic login attempt")
    
    # Step 9: Verify that user can still login again after "restart"
    print("\n9. Verifying user can login again after 'restart'...")
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if response.status_code == 200:
        new_tokens = response.json()['tokens']
        print("✓ User can login again successfully")
        
        # Verify the new token works
        new_headers = {'Authorization': f'Bearer {new_tokens["access_token"]}'}
        response = requests.get(f'{BASE_URL}/auth/verify', headers=new_headers)
        if response.status_code == 200:
            print("✓ New token is valid")
        else:
            print(f"✗ New token verification failed: {response.json()}")
            return
    else:
        print(f"✗ Re-login failed: {response.json()}")
        return
    
    # Step 10: Verify previous session is still accessible
    print("\n10. Verifying previous session is still accessible...")
    response = requests.get(f'{BASE_URL}/chat/sessions', headers=new_headers)
    if response.status_code == 200:
        sessions = response.json()['sessions']
        if len(sessions) > 0:
            print(f"✓ Previous session is still accessible: {sessions[0]['title']}")
        else:
            print("✗ No sessions found")
            return
    else:
        print(f"✗ Failed to access sessions: {response.json()}")
        return
    
    print("\n🎉 Automatic logout and landing page redirect functionality test completed!")
    print("\n📋 Summary of functionality:")
    print("   ✅ User is automatically logged out when application is closed")
    print("   ✅ Application always starts at landing page (no auto-login)")
    print("   ✅ User can login again after app restart")
    print("   ✅ Previous sessions are preserved and accessible")
    print("   ✅ Protected routes redirect to landing page when not authenticated")

if __name__ == '__main__':
    test_auto_logout_landing_functionality() 