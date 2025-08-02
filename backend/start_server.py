#!/usr/bin/env python3
"""
Startup script for the backend server with agent diagnostics
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'crewai',
        'google-generativeai',
        'tavily',
        'qdrant-client'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_environment_vars():
    """Check if required environment variables are set"""
    print("\n🌍 Checking environment variables...")
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API key',
        'TAVILY_API_KEY': 'Tavily search API key',
        'JWT_SECRET_KEY': 'JWT secret for authentication',
        'DATABASE_URL': 'Database connection string'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} ({description}) - MISSING")
        else:
            print(f"✅ {var} - FOUND")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    return True

def initialize_agents():
    """Initialize agents and check their status"""
    print("\n🤖 Initializing agents...")
    
    try:
        # Import agent modules
        from agents import agents, get_agent_status, update_agent_status
        
        # Initialize agent statuses
        agent_types = ["multimodal", "chat", "document", "research", "lightweight"]
        
        for agent_type in agent_types:
            try:
                update_agent_status(agent_type, "online")
                print(f"✅ {agent_type} agent status set to online")
            except Exception as e:
                print(f"❌ Failed to set {agent_type} status: {e}")
        
        # Check agent status
        statuses = get_agent_status()
        print(f"Agent statuses: {statuses}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        traceback.print_exc()
        return False

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting server...")
    
    try:
        from app import app
        
        # Get port from environment or default to 8000
        port = int(os.environ.get('PORT', 8000))
        
        print(f"Starting server on port {port}")
        print("Press Ctrl+C to stop the server")
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    print("🚀 Backend Server Startup")
    print("=" * 40)
    
    # Run checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment_vars),
        ("Agents", initialize_agents)
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All checks passed! Starting server...")
        start_server()
    else:
        print("\n❌ Some checks failed. Please fix the issues above before starting the server.")
        print("\nQuick fixes:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check your .env file for missing variables")
        print("3. Make sure all API keys are valid")

if __name__ == "__main__":
    main() 