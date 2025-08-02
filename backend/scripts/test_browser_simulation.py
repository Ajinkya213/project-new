#!/usr/bin/env python3
"""
Test to simulate browser behavior
"""

import requests
import json

def test_browser_simulation():
    """Test to simulate browser behavior"""
    base_url = "http://localhost:8000"
    
    print("🌐 Simulating browser behavior...")
    
    # Test data
    login_data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    try:
        # Simulate browser request with proper headers
        print("1. Testing browser-like request...")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Origin": "http://localhost:5173",  # Common Vite dev server port
            "Referer": "http://localhost:5173/"
        }
        
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_different_ports():
    """Test with different frontend ports"""
    base_url = "http://localhost:8000"
    
    print("\n🔌 Testing different frontend ports...")
    
    ports = [3000, 5173, 4173, 8080]
    
    for port in ports:
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": f"http://localhost:{port}"
            }
            
            response = requests.post(
                f"{base_url}/auth/login",
                json={"username": "testuser", "password": "TestPass123!"},
                headers=headers
            )
            
            print(f"Port {port}: Status {response.status_code}")
            
        except Exception as e:
            print(f"Port {port}: Error {e}")

if __name__ == "__main__":
    test_browser_simulation()
    test_different_ports() 