#!/usr/bin/env python3
"""
Script to help update .env file with missing API keys
"""

import os
from pathlib import Path

def update_env_file():
    """Update .env file with missing variables"""
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check what's missing
    missing_vars = []
    
    if 'GOOGLE_API_KEY=' not in content:
        missing_vars.append('GOOGLE_API_KEY=your_google_api_key_here')
    
    if 'TAVILY_API_KEY=' not in content:
        missing_vars.append('TAVILY_API_KEY=your_tavily_api_key_here')
    
    if missing_vars:
        print("🔧 Adding missing environment variables to .env file...")
        
        # Add missing variables
        new_content = content.strip() + "\n\n# Agent API Keys\n"
        for var in missing_vars:
            new_content += f"{var}\n"
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated .env file with missing variables")
        print("\n📝 Please edit the .env file and replace:")
        for var in missing_vars:
            print(f"   {var}")
        print("\nWith your actual API keys:")
        print("1. Get Google API key from: https://makersuite.google.com/app/apikey")
        print("2. Get Tavily API key from: https://tavily.com/")
        
        return True
    else:
        print("✅ All required variables are already in .env file")
        return True

def check_current_env():
    """Check current environment variables"""
    print("\n🔍 Current Environment Variables:")
    print("=" * 40)
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API',
        'TAVILY_API_KEY': 'Tavily Search API',
        'JWT_SECRET_KEY': 'JWT Secret',
        'DATABASE_URL': 'Database URL'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "your_google_api_key_here" and value != "your_tavily_api_key_here":
            print(f"✅ {var}: {description} - SET")
            if var in ['GOOGLE_API_KEY', 'TAVILY_API_KEY']:
                print(f"   Value: {value[:10]}...")
        else:
            print(f"❌ {var}: {description} - MISSING or INVALID")
            all_good = False
    
    return all_good

def main():
    """Main function"""
    print("🔧 Environment Variable Updater")
    print("=" * 40)
    
    # Update .env file
    updated = update_env_file()
    
    if updated:
        print("\n📋 Next Steps:")
        print("1. Edit the .env file in your text editor")
        print("2. Replace the placeholder values with your actual API keys")
        print("3. Save the file")
        print("4. Run: python setup_env.py")
        print("5. Start the server: python app.py")
        
        print("\n💡 Example .env file should look like:")
        print("GOOGLE_API_KEY=AIzaSyC...")
        print("TAVILY_API_KEY=tvly-...")
        # print("JWT_SECRET_KEY=30d850b701fd6f699b2f7edfdaac5a27e9a0d68eceec31bee2f366050fa0ddf8")
        print("DATABASE_URL=sqlite:///chat_app.db")

if __name__ == "__main__":
    main() 
