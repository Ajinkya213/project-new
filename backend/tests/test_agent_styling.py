#!/usr/bin/env python3
"""
Test script to demonstrate agent styling and automatic selection
"""

import requests
import json

def test_agent_styling():
    """Test the agent styling with various queries"""
    
    # Test configuration
    BASE_URL = "http://localhost:8000"
    API_BASE = f"{BASE_URL}/api"
    
    # Test queries that should trigger different agents
    test_queries = [
        {
            "query": "Hello, how are you?",
            "expected_agent": "chat",
            "description": "Chat query"
        },
        {
            "query": "What is artificial intelligence?",
            "expected_agent": "research", 
            "description": "Research query"
        },
        {
            "query": "Analyze this document for key points",
            "expected_agent": "document",
            "description": "Document analysis query"
        },
        {
            "query": "Search the uploaded documents for AI information",
            "expected_agent": "multimodal",
            "description": "Multimodal query"
        },
        {
            "query": "Random query that doesn't match any specific agent",
            "expected_agent": "lightweight",
            "description": "Fallback query"
        }
    ]
    
    print("🎨 Testing Agent Styling and Selection")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Query: '{test_case['query']}'")
        print(f"   Expected Agent: {test_case['expected_agent']}")
        
        try:
            # Test the auto-query endpoint
            response = requests.post(
                f"{API_BASE}/agent/auto-query",
                headers={'Content-Type': 'application/json'},
                json={'query': test_case['query']}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    selected_agent = data.get('agent_selection', {}).get('selected_agent', 'unknown')
                    confidence = data.get('agent_selection', {}).get('confidence', 0)
                    response_text = data.get('response', 'No response')
                    
                    print(f"   ✅ Selected Agent: {selected_agent}")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   💬 Response: {response_text[:100]}...")
                    
                    # Check if the expected agent was selected
                    if selected_agent == test_case['expected_agent']:
                        print(f"   🎯 Correct agent selected!")
                    else:
                        print(f"   ⚠️  Expected {test_case['expected_agent']}, got {selected_agent}")
                else:
                    print(f"   ❌ Query failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 40)

def test_agent_colors():
    """Show the color scheme for different agents"""
    
    print("\n🎨 Agent Color Scheme")
    print("=" * 30)
    
    agents = [
        ("multimodal", "🔗 Multimodal", "Blue"),
        ("research", "🔍 Research", "Green"), 
        ("document", "📄 Document", "Purple"),
        ("chat", "💬 Chat", "Orange"),
        ("lightweight", "⚡ Lightweight", "Gray")
    ]
    
    for agent_type, display_name, color in agents:
        print(f"   {display_name}: {color} theme")
    
    print("\nEach agent will have:")
    print("   • Unique color-coded badge")
    print("   • Appropriate icon")
    print("   • Confidence percentage")
    print("   • Styled message bubbles")

if __name__ == "__main__":
    test_agent_styling()
    test_agent_colors() 