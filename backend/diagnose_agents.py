#!/usr/bin/env python3
"""
Diagnostic script to check agent status and identify issues
"""

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    
    try:
        from agents import agents, get_agent_by_type, get_agent_status
        print("✅ Agents module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import agents module: {e}")
        return False
    
    try:
        from services.query_service import QueryService
        print("✅ QueryService imported successfully")
    except Exception as e:
        print(f"❌ Failed to import QueryService: {e}")
        return False
    
    try:
        from services.agent_selector import agent_selector
        print("✅ AgentSelector imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AgentSelector: {e}")
        return False
    
    try:
        from crewai import Agent, Task, Crew
        print("✅ CrewAI imported successfully")
    except Exception as e:
        print(f"❌ Failed to import CrewAI: {e}")
        return False
    
    return True

def check_agent_initialization():
    """Check if agents can be initialized"""
    print("\n🤖 Checking agent initialization...")
    
    try:
        from agents import agents, get_agent_by_type
        
        # Check if agents dictionary is populated
        print(f"Available agents: {list(agents.keys())}")
        
        # Test getting each agent
        for agent_type in ["multimodal", "chat", "document", "research", "lightweight"]:
            try:
                agent = get_agent_by_type(agent_type)
                if agent:
                    print(f"✅ {agent_type} agent loaded successfully")
                else:
                    print(f"❌ {agent_type} agent returned None")
            except Exception as e:
                print(f"❌ Failed to load {agent_type} agent: {e}")
                
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def check_query_service():
    """Check if QueryService can be initialized"""
    print("\n🔧 Checking QueryService...")
    
    try:
        from services.query_service import QueryService
        
        # Initialize the service
        query_service = QueryService()
        print("✅ QueryService initialized successfully")
        
        # Check health
        health = query_service.health_check()
        print(f"Health check result: {health}")
        
        return True
        
    except Exception as e:
        print(f"❌ QueryService initialization failed: {e}")
        traceback.print_exc()
        return False

def check_agent_selector():
    """Check if AgentSelector works"""
    print("\n🎯 Checking AgentSelector...")
    
    try:
        from services.agent_selector import agent_selector
        
        # Test with a simple query
        test_query = "Hello, how are you?"
        reasoning = agent_selector.get_agent_reasoning(test_query)
        
        print(f"Test query: '{test_query}'")
        print(f"Selected agent: {reasoning['selected_agent']}")
        print(f"Confidence: {reasoning['confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentSelector failed: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """Check environment variables and configuration"""
    print("\n🌍 Checking environment...")
    
    # Check required environment variables
    required_vars = [
        'GOOGLE_API_KEY',
        'TAVILY_API_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"⚠️  Missing: {var}")
        else:
            print(f"✅ Found: {var}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file")
        return False
    
    return True

def main():
    """Run all diagnostics"""
    print("🔧 Agent Diagnostic Tool")
    print("=" * 40)
    
    checks = [
        ("Environment", check_environment),
        ("Imports", check_imports),
        ("Agent Initialization", check_agent_initialization),
        ("Query Service", check_query_service),
        ("Agent Selector", check_agent_selector)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    print("\n📊 Summary:")
    print("=" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Agents should be working.")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main() 