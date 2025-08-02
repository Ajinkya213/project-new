#!/usr/bin/env python3
"""
Environment setup script for the chat application
"""

import os
from pathlib import Path

def create_env_template():
    """Create a .env template file"""
    
    env_content = """# Chat Application Environment Variables
# Copy this file to .env and fill in your API keys

# Google Gemini API Key (Required)
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Tavily Search API Key (Required for web search)
# Get from: https://tavily.com/
TAVILY_API_KEY=your_tavily_api_key_here

# JWT Secret Key (Required for authentication)
# Generate a random string for this
JWT_SECRET_KEY=your_jwt_secret_key_here

# Database URL (Required)
# Format: mysql+pymysql://username:password@host:port/database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/chat_app

# Optional: Server Configuration
PORT=8000
DEBUG=True

# Optional: CORS Origins
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        print("Please check if it contains the required variables:")
        print("  - GOOGLE_API_KEY")
        print("  - TAVILY_API_KEY") 
        print("  - JWT_SECRET_KEY")
        print("  - DATABASE_URL")
    else:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env template file")
        print("Please edit .env and add your API keys")
    
    return env_file.exists()

def check_env_vars():
    """Check which environment variables are set"""
    print("\n🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API',
        'TAVILY_API_KEY': 'Tavily Search API', 
        'JWT_SECRET_KEY': 'JWT Secret',
        'DATABASE_URL': 'Database URL'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - SET")
            if var in ['GOOGLE_API_KEY', 'TAVILY_API_KEY']:
                print(f"   Value: {value[:10]}...")
        else:
            print(f"❌ {var}: {description} - MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {missing_vars}")
        print("\nTo fix this:")
        print("1. Get Google API key from: https://makersuite.google.com/app/apikey")
        print("2. Get Tavily API key from: https://tavily.com/")
        print("3. Generate a JWT secret (any random string)")
        print("4. Set up your database and get the connection URL")
        print("5. Add all variables to your .env file")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def test_api_keys():
    """Test if the API keys are working"""
    print("\n🔑 Testing API Keys")
    print("=" * 30)
    
    # Test Google API
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and google_key != "your_google_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            # Try to create a model instance
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Google API key is valid")
        except Exception as e:
            print(f"❌ Google API key error: {e}")
    else:
        print("❌ Google API key not set or invalid")
    
    # Test Tavily API
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key != "your_tavily_api_key_here":
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            # Try a simple search
            result = client.search(query="test", max_results=1)
            print("✅ Tavily API key is valid")
        except Exception as e:
            print(f"❌ Tavily API key error: {e}")
    else:
        print("❌ Tavily API key not set or invalid")

def main():
    """Main setup function"""
    print("🚀 Environment Setup for Chat Application")
    print("=" * 50)
    
    # Create .env template if needed
    env_exists = create_env_template()
    
    # Check current environment
    env_ok = check_env_vars()
    
    if env_ok:
        # Test API keys
        test_api_keys()
        print("\n🎉 Environment is ready!")
        print("You can now start the server with: python app.py")
    else:
        print("\n📝 Next steps:")
        print("1. Edit the .env file with your API keys")
        print("2. Run this script again to verify")
        print("3. Start the server with: python app.py")

if __name__ == "__main__":
    main() 