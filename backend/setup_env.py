#!/usr/bin/env python3
"""
Environment Setup Script
Creates .env file with default configuration
"""

import os

def create_env_file():
    """Create .env file with default configuration"""
    
    env_content = """# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///chat_app.db

# Server Configuration
PORT=8000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("⚠️  Using SQLite database for development")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 