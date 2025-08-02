#!/usr/bin/env python3
"""
Test script to validate web search functionality
"""

import os
from dotenv import load_dotenv
from tavily import TavilyClient

def test_tavily_api_key():
    """Test if Tavily API key is valid"""
    print("🔍 Testing Tavily API Key")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key or api_key == "your-tavily-api-key-here":
        print("❌ TAVILY_API_KEY not set or using placeholder")
        print("📝 Please set your Tavily API key in the .env file")
        return False
    
    print(f"✅ TAVILY_API_KEY found: {api_key[:10]}...")
    
    # Test API key
    try:
        client = TavilyClient(api_key=api_key)
        # Try a simple search
        results = client.search(query="test", max_results=1)
        print("✅ Tavily API key is valid!")
        print(f"📊 Search results: {len(results.get('results', []))} found")
        return True
    except Exception as e:
        print(f"❌ Tavily API key validation failed: {e}")
        return False

def test_raw_tavily_search():
    """Test raw Tavily search functionality"""
    print("\n🔍 Testing Raw Tavily Search")
    print("=" * 50)
    
    try:
        load_dotenv()
        api_key = os.getenv("TAVILY_API_KEY")
        client = TavilyClient(api_key=api_key)
        
        # Test search
        print("🔍 Testing search for 'artificial intelligence'...")
        results = client.search(query="artificial intelligence", max_results=3)
        
        if results and 'results' in results:
            print("✅ Raw Tavily search working!")
            print(f"📊 Found {len(results['results'])} results")
            for i, result in enumerate(results['results'][:2], 1):
                print(f"📄 Result {i}: {result.get('title', 'No title')}")
                print(f"   URL: {result.get('url', 'No URL')}")
                print(f"   Content: {result.get('content', 'No content')[:100]}...")
            return True
        else:
            print("❌ No results returned from Tavily")
            return False
            
    except Exception as e:
        print(f"❌ Raw Tavily search failed: {e}")
        return False

def test_web_search_function():
    """Test the web search function directly"""
    print("\n🔍 Testing Web Search Function")
    print("=" * 50)
    
    try:
        # Import the raw function (not the tool)
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        # Get the raw function from the module
        import agents.tools
        import inspect
        
        # Find the raw search function
        for name, obj in inspect.getmembers(agents.tools):
            if inspect.isfunction(obj) and name == 'search_web_raw':
                print("🔍 Testing raw search function...")
                result = obj("artificial intelligence")
                print("✅ Raw search function working!")
                print(f"📄 Response length: {len(result)} characters")
                print(f"📝 Preview: {result[:200]}...")
                return True
        
        print("❌ Raw search function not found")
        return False
            
    except Exception as e:
        print(f"❌ Web search function test failed: {e}")
        return False

def test_agent_web_search():
    """Test web search through agent"""
    print("\n🤖 Testing Agent Web Search")
    print("=" * 50)
    
    try:
        from services.query_service import QueryService
        
        # Initialize query service
        query_service = QueryService()
        
        # Test research agent with web search
        print("🔍 Testing research agent with web search...")
        result = query_service.process_query("What is the latest news about AI?")
        
        if result.get('success'):
            print("✅ Agent web search working!")
            print(f"📄 Response: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"❌ Agent web search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Agent web search test failed: {e}")
        return False

def test_web_search_tool():
    """Test the web search tool properly"""
    print("\n🔧 Testing Web Search Tool")
    print("=" * 50)
    
    try:
        from agents.tools import search_web
        
        # Test the tool's run method
        print("🔍 Testing web search tool...")
        result = search_web.run("artificial intelligence")
        
        if "Search failed" in result:
            print(f"❌ Search failed: {result}")
            return False
        else:
            print("✅ Web search tool working!")
            print(f"📄 Response length: {len(result)} characters")
            print(f"📝 Preview: {result[:200]}...")
            return True
            
    except Exception as e:
        print(f"❌ Web search tool test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🌐 Web Search Validation")
    print("=" * 50)
    
    # Test 1: API Key
    api_key_valid = test_tavily_api_key()
    
    # Test 2: Raw Tavily Search
    raw_search_valid = test_raw_tavily_search()
    
    # Test 3: Web Search Tool
    tool_valid = test_web_search_tool()
    
    # Test 4: Agent Web Search
    agent_valid = test_agent_web_search()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"API Key Valid: {'✅' if api_key_valid else '❌'}")
    print(f"Raw Tavily Search: {'✅' if raw_search_valid else '❌'}")
    print(f"Web Search Tool: {'✅' if tool_valid else '❌'}")
    print(f"Agent Web Search: {'✅' if agent_valid else '❌'}")
    
    if api_key_valid and raw_search_valid and tool_valid and agent_valid:
        print("\n🎉 All web search tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main() 