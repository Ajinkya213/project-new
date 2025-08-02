#!/usr/bin/env python3
"""
Test script to check .env file loading
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """Test if .env file is being loaded"""
    print("🔍 Testing .env file loading")
    print("=" * 40)
    
    # Load .env file
    load_dotenv()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Read .env file content
        with open('.env', 'r') as f:
            content = f.read()
            print(f"📄 .env file size: {len(content)} characters")
            
            # Check for API keys in content
            if 'GOOGLE_API_KEY' in content:
                print("✅ GOOGLE_API_KEY found in .env file")
            else:
                print("❌ GOOGLE_API_KEY NOT found in .env file")
                
            if 'TAVILY_API_KEY' in content:
                print("✅ TAVILY_API_KEY found in .env file")
            else:
                print("❌ TAVILY_API_KEY NOT found in .env file")
    else:
        print("❌ .env file does not exist")
        return False
    
    # Check environment variables
    print("\n🔍 Environment Variables:")
    print("=" * 30)
    
    google_key = os.getenv('GOOGLE_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')
    jwt_key = os.getenv('JWT_SECRET_KEY')
    db_url = os.getenv('DATABASE_URL')
    
    print(f"GOOGLE_API_KEY: {'SET' if google_key else 'MISSING'}")
    print(f"TAVILY_API_KEY: {'SET' if tavily_key else 'MISSING'}")
    print(f"JWT_SECRET_KEY: {'SET' if jwt_key else 'MISSING'}")
    print(f"DATABASE_URL: {'SET' if db_url else 'MISSING'}")
    
    if google_key and tavily_key:
        print("\n✅ All API keys are set!")
        return True
    else:
        print("\n❌ Some API keys are missing")
        return False

def add_api_keys_to_env():
    """Add API keys to .env file"""
    print("\n🔧 Adding API keys to .env file...")
    
    # Read current content
    with open('.env', 'r') as f:
        content = f.read()
    
    # Add API keys if they don't exist
    if 'GOOGLE_API_KEY=' not in content:
        content += "\n# Agent API Keys\nGOOGLE_API_KEY=your_google_api_key_here\n"
    
    if 'TAVILY_API_KEY=' not in content:
        content += "TAVILY_API_KEY=your_tavily_api_key_here\n"
    
    # Write back to file
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Added API key placeholders to .env file")
    print("📝 Please edit .env file and replace the placeholder values with your actual API keys")

if __name__ == "__main__":
    test_env_loading()
    add_api_keys_to_env() 