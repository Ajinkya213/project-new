#!/usr/bin/env python3
"""
Test script to verify all agents are working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.query_service import query_service
import time

def test_agent_loading():
    """Test if all agents can be loaded"""
    print("🧪 Testing Agent Loading")
    print("=" * 40)
    
    all_agents = ["multimodal", "chat", "document", "research", "lightweight"]
    
    for agent_type in all_agents:
        print(f"\nTesting {agent_type} agent...")
        try:
            agent = query_service._get_agent(agent_type)
            if agent:
                print(f"✅ {agent_type} agent loaded successfully")
                print(f"   Agent type: {type(agent).__name__}")
            else:
                print(f"❌ {agent_type} agent failed to load")
        except Exception as e:
            print(f"❌ {agent_type} agent error: {e}")

def test_agent_health():
    """Test agent health endpoint"""
    print("\n🧪 Testing Agent Health")
    print("=" * 40)
    
    try:
        health = query_service.health_check()
        print(f"Health Status: {health['status']}")
        print(f"Available Agents: {health['available_agents']}")
        print(f"Total Agents: {health['total_agents']}")
        print(f"Online Agents: {health['online_agents']}")
        
        if health['agent_statuses']:
            print("\nAgent Statuses:")
            for agent_type, status in health['agent_statuses'].items():
                print(f"  {agent_type}: {status['status']}")
        
        return health
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return None

def test_agent_queries():
    """Test agent queries"""
    print("\n🧪 Testing Agent Queries")
    print("=" * 40)
    
    test_queries = [
        "Hello, how are you?",
        "What is artificial intelligence?",
        "Can you help me with a document?",
        "Tell me about the weather"
    ]
    
    all_agents = ["multimodal", "chat", "document", "research", "lightweight"]
    
    for agent_type in all_agents:
        print(f"\nTesting {agent_type} agent queries...")
        for i, query in enumerate(test_queries[:2]):  # Test first 2 queries per agent
            print(f"  Query {i+1}: {query}")
            try:
                result = query_service.process_query(query, agent_type)
                if result['success']:
                    print(f"    ✅ Query successful")
                    print(f"    Response: {result['response'][:100]}...")
                    print(f"    Response time: {result.get('response_time', 'N/A')}s")
                else:
                    print(f"    ❌ Query failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"    ❌ Query error: {e}")

def test_agent_tools():
    """Test agent tools"""
    print("\n🧪 Testing Agent Tools")
    print("=" * 40)
    
    try:
        from agents.tools import search_web, retrieve_from_document
        
        # Test web search
        print("Testing web search tool...")
        web_result = search_web.func("artificial intelligence")
        print(f"Web search result: {web_result[:100]}...")
        
        # Test document retrieval
        print("Testing document retrieval tool...")
        doc_result = retrieve_from_document.func("test query")
        print(f"Document retrieval result: {doc_result[:100]}...")
        
    except Exception as e:
        print(f"❌ Tool testing failed: {e}")

def test_agent_tasks():
    """Test agent tasks"""
    print("\n🧪 Testing Agent Tasks")
    print("=" * 40)
    
    try:
        from agents.tasks import build_task, build_chat_task, build_document_task, build_research_task, build_lightweight_task
        
        test_query = "Test query for task building"
        
        # Test task building
        print("Testing task building...")
        multimodal_task = build_task(test_query)
        chat_task = build_chat_task(test_query)
        document_task = build_document_task(test_query)
        research_task = build_research_task(test_query)
        lightweight_task = build_lightweight_task(test_query)
        
        print(f"✅ All tasks built successfully")
        print(f"  Multimodal task: {multimodal_task.description}")
        print(f"  Chat task: {chat_task.description}")
        print(f"  Document task: {document_task.description}")
        print(f"  Research task: {research_task.description}")
        print(f"  Lightweight task: {lightweight_task.description}")
        
    except Exception as e:
        print(f"❌ Task testing failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Agent Tests")
    print("=" * 50)
    
    # Test agent loading
    test_agent_loading()
    
    # Test health check
    health = test_agent_health()
    
    # Test agent queries
    test_agent_queries()
    
    # Test agent tools
    test_agent_tools()
    
    # Test agent tasks
    test_agent_tasks()
    
    print("\n" + "=" * 50)
    print("🎉 Agent testing completed!")
    
    if health:
        print(f"📊 Summary:")
        print(f"   - Available agents: {len(health['available_agents'])}")
        print(f"   - Online agents: {health['online_agents']}")
        print(f"   - Overall status: {health['status']}")

if __name__ == "__main__":
    main() 