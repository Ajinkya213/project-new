#!/usr/bin/env python3
"""
Test script to demonstrate automatic agent selection
"""

from services.agent_selector import agent_selector

def test_agent_selection():
    """Test automatic agent selection with various queries"""
    
    test_queries = [
        # Chat queries
        "Hello, how are you?",
        "Hi there!",
        "Thanks for your help",
        "Can you assist me?",
        
        # Research queries
        "What is artificial intelligence?",
        "Research the latest developments in machine learning",
        "Tell me about current trends in technology",
        "What are the benefits of renewable energy?",
        
        # Document queries
        "Analyze this document for key points",
        "Summarize the uploaded PDF",
        "Extract insights from the file",
        "What are the main findings in this document?",
        
        # Multimodal queries
        "Search the uploaded documents for information about AI",
        "Find the document that mentions machine learning",
        "Look up information in the stored files",
        "Retrieve data from the uploaded PDF",
        
        # Mixed queries
        "Can you help me research AI and also analyze this document?",
        "Hello! I need to find information about machine learning in my documents",
        "Please assist me with researching current trends and analyzing my files"
    ]
    
    print("🤖 Testing Automatic Agent Selection")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Get agent selection reasoning
        reasoning = agent_selector.get_agent_reasoning(query)
        
        print(f"   Selected Agent: {reasoning['selected_agent']}")
        print(f"   Confidence: {reasoning['confidence']:.2f}")
        print(f"   Top 3 Agents:")
        for agent, score in reasoning['top_agents'][:3]:
            print(f"     - {agent}: {score:.2f}")
        
        print("-" * 40)

def test_agent_scoring():
    """Test individual agent scoring"""
    
    test_query = "Research artificial intelligence and analyze the uploaded documents"
    
    print("\n🔍 Testing Agent Scoring")
    print("=" * 30)
    print(f"Query: '{test_query}'")
    
    scores = agent_selector.analyze_query(test_query)
    
    print("\nAgent Scores:")
    for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {agent}: {score:.3f}")

if __name__ == "__main__":
    test_agent_selection()
    test_agent_scoring() 