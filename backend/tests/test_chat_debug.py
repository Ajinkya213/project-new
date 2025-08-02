#!/usr/bin/env python3
"""
Test script to debug chat message issues
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_chat_message():
    """Test adding a chat message"""
    
    # First, let's test if the server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Server health check: {response.status_code}")
    except Exception as e:
        print(f"Server not running: {e}")
        return
    
    # Test data
    test_data = {
        "text": "Hello, this is a test message",
        "sender": "ai"
    }
    
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    # Test the message validation
    from utils.validators import MessageValidator
    is_valid, error_msg = MessageValidator.validate_message(test_data["text"])
    print(f"Message validation: {is_valid}, Error: {error_msg}")
    
    # Test suspicious content detection
    from utils.validators import MessageValidator
    has_suspicious = MessageValidator._contains_suspicious_content(test_data["text"])
    print(f"Contains suspicious content: {has_suspicious}")

if __name__ == "__main__":
    test_chat_message() 