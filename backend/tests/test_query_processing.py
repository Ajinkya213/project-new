#!/usr/bin/env python3
"""
Test script to debug query processing issues
"""

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_query():
    """Test a simple query to see what happens"""
    print("🧪 Testing Simple Query Processing")
    print("=" * 40)
    
    try:
        from services.query_service import QueryService
        
        # Initialize the service
        query_service = QueryService()
        print("✅ QueryService initialized")
        
        # Test a simple query
        test_query = "Hello, how are you?"
        print(f"Test query: '{test_query}'")
        
        # Test auto agent selection
        agent_selection = query_service.auto_select_agent(test_query)
        print(f"Selected agent: {agent_selection['selected_agent']}")
        print(f"Confidence: {agent_selection['confidence']}")
        
        # Test query processing
        print("\n🔄 Processing query...")
        result = query_service.process_query(test_query, agent_selection['selected_agent'])
        
        print(f"Success: {result.get('success')}")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Agent type: {result.get('agent_type')}")
        print(f"Response time: {result.get('response_time')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        traceback.print_exc()
        return False

def test_agent_initialization():
    """Test agent initialization"""
    print("\n🤖 Testing Agent Initialization")
    print("=" * 40)
    
    try:
        from agents import agents, get_agent_by_type
        
        print(f"Available agents: {list(agents.keys())}")
        
        # Test each agent
        for agent_type in ["multimodal", "chat", "document", "research", "lightweight"]:
            try:
                agent = get_agent_by_type(agent_type)
                if agent:
                    print(f"✅ {agent_type} agent loaded")
                    # Test agent properties
                    print(f"   Role: {agent.role}")
                    print(f"   Goal: {agent.goal}")
                else:
                    print(f"❌ {agent_type} agent is None")
            except Exception as e:
                print(f"❌ {agent_type} agent failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🌍 Testing Environment")
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
        if value:
            print(f"✅ {var}: {description} - FOUND")
            if var in ['GOOGLE_API_KEY', 'TAVILY_API_KEY']:
                # Show first few characters to verify it's not empty
                print(f"   Value: {value[:10]}...")
        else:
            print(f"❌ {var}: {description} - MISSING")
            all_good = False
    
    return all_good

def test_api_keys():
    """Test if API keys are working"""
    print("\n🔑 Testing API Keys")
    print("=" * 40)
    
    try:
        import google.generativeai as genai
        
        # Test Google API
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                genai.configure(api_key=google_key)
                # Try to create a simple model instance
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Google API key is valid")
            except Exception as e:
                print(f"❌ Google API key error: {e}")
        else:
            print("❌ Google API key not found")
        
        # Test Tavily API
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=tavily_key)
                # Try a simple search
                result = client.search(query="test", max_results=1)
                print("✅ Tavily API key is valid")
            except Exception as e:
                print(f"❌ Tavily API key error: {e}")
        else:
            print("❌ Tavily API key not found")
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🔧 Query Processing Diagnostic")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("API Keys", test_api_keys),
        ("Agent Initialization", test_agent_initialization),
        ("Query Processing", test_simple_query)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            results.append((name, False))
    
    print("\n📊 Summary:")
    print("=" * 30)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Query processing should work.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main() 