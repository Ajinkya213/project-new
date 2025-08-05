#!/usr/bin/env python3
"""
Task Building Logic - Factory Pattern for Task Creation
Implements task building functions for different agent types and query types
"""

from typing import Dict, Any, List, Optional
from crewai import Task
from datetime import datetime

def build_task(description: str, agent, context: Dict = None) -> Task:
    """
    Build a general task for any agent
    
    Args:
        description: Task description
        agent: Agent instance
        context: Additional context
        
    Returns:
        Task instance
    """
    return Task(
        description=description,
        agent=agent,
        context=context or {},
        expected_output="A comprehensive response to the user's query"
    )

def build_document_processing_task(document_data: List[Dict]) -> Task:
    """
    Build task for document processing
    
    Args:
        document_data: List of document data to process
        
    Returns:
        Task instance for document processing
    """
    from agents.agents import create_document_agent
    
    agent = create_document_agent()
    
    description = f"""
    Process and analyze the following documents:
    
    Documents to process: {len(document_data)} documents
    
    For each document:
    1. Extract key information and insights
    2. Identify important sections and topics
    3. Create a summary of the content
    4. Index the content for future retrieval
    
    Document data: {document_data[:3]}  # First 3 documents for context
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'document_data': document_data},
        expected_output="Document processing results with extracted information and insights"
    )

def build_document_query_task(query: str, document_context: List[Dict] = None) -> Task:
    """
    Build task for document query processing
    
    Args:
        query: User query about documents
        document_context: Relevant document context
        
    Returns:
        Task instance for document query
    """
    from agents.agents import create_document_agent
    
    agent = create_document_agent()
    
    description = f"""
    Answer the following query based on the available documents:
    
    Query: {query}
    
    Document Context: {document_context or 'No specific document context provided'}
    
    Please:
    1. Search through the available documents for relevant information
    2. Extract and synthesize the information that answers the query
    3. Provide a comprehensive and accurate response
    4. Include relevant citations or references to document sections
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'document_context': document_context},
        expected_output="A detailed response based on document content with relevant citations"
    )

def build_web_search_task(query: str, search_context: Dict = None) -> Task:
    """
    Build task for web search queries
    
    Args:
        query: User query for web search
        search_context: Additional search context
        
    Returns:
        Task instance for web search
    """
    from agents.agents import create_web_search_agent
    
    agent = create_web_search_agent()
    
    description = f"""
    Conduct a comprehensive web search for the following query:
    
    Query: {query}
    
    Search Context: {search_context or 'No specific context provided'}
    
    Please:
    1. Search the web for current and relevant information
    2. Analyze and synthesize the search results
    3. Provide a comprehensive answer with multiple sources
    4. Include relevant citations and links
    5. Ensure the information is current and accurate
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'search_context': search_context},
        expected_output="A comprehensive response based on web search results with citations"
    )

def build_multimodal_task(query: str, image_context: List[str] = None) -> Task:
    """
    Build task for multimodal queries (text + images)
    
    Args:
        query: User query
        image_context: List of image paths or descriptions
        
    Returns:
        Task instance for multimodal processing
    """
    from agents.agents import create_multimodal_agent
    
    agent = create_multimodal_agent()
    
    description = f"""
    Process the following multimodal query:
    
    Query: {query}
    
    Image Context: {image_context or 'No images provided'}
    
    Please:
    1. Analyze any provided images or visual content
    2. Process the text query in context of the visual information
    3. Provide insights that combine both text and visual analysis
    4. Identify key elements in images and their relevance to the query
    5. Generate a comprehensive response that addresses both text and visual aspects
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'image_context': image_context},
        expected_output="A comprehensive response that combines text and visual analysis"
    )

def build_research_task(query: str, research_context: Dict = None) -> Task:
    """
    Build task for comprehensive research queries
    
    Args:
        query: Research query
        research_context: Additional research context
        
    Returns:
        Task instance for research
    """
    from agents.agents import create_research_agent
    
    agent = create_research_agent()
    
    description = f"""
    Conduct comprehensive research on the following topic:
    
    Research Query: {query}
    
    Research Context: {research_context or 'No specific context provided'}
    
    Please:
    1. Conduct thorough research from multiple sources
    2. Analyze and synthesize the information
    3. Provide a detailed and well-structured response
    4. Include relevant citations and references
    5. Consider different perspectives and viewpoints
    6. Provide insights and conclusions based on the research
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'research_context': research_context},
        expected_output="A comprehensive research report with detailed analysis and citations"
    )

def build_lightweight_task(query: str, context: Dict = None) -> Task:
    """
    Build task for lightweight, fast responses
    
    Args:
        query: User query
        context: Additional context
        
    Returns:
        Task instance for lightweight processing
    """
    from agents.agents import create_lightweight_agent
    
    agent = create_lightweight_agent()
    
    description = f"""
    Provide a quick and accurate response to the following query:
    
    Query: {query}
    
    Context: {context or 'No specific context provided'}
    
    Please:
    1. Provide a concise and accurate response
    2. Focus on the most relevant information
    3. Keep the response clear and helpful
    4. If the query requires more detailed analysis, suggest using a specialized agent
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'context': context},
        expected_output="A quick, accurate, and helpful response"
    )

def build_chat_task(query: str, chat_context: Dict = None) -> Task:
    """
    Build task for conversational chat
    
    Args:
        query: User message
        chat_context: Chat history and context
        
    Returns:
        Task instance for chat
    """
    from agents.agents import create_lightweight_agent
    
    agent = create_lightweight_agent()
    
    description = f"""
    Engage in a helpful conversation with the user:
    
    User Message: {query}
    
    Chat Context: {chat_context or 'No previous context'}
    
    Please:
    1. Provide a helpful and engaging response
    2. Maintain a conversational tone
    3. Ask clarifying questions if needed
    4. Provide relevant information and insights
    5. Keep the response appropriate for the context
    """
    
    return Task(
        description=description,
        agent=agent,
        context={'query': query, 'chat_context': chat_context},
        expected_output="A helpful and engaging conversational response"
    )

def get_task_builder(agent_type: str):
    """
    Get appropriate task builder function for agent type
    
    Args:
        agent_type: Type of agent
        
    Returns:
        Task builder function
    """
    task_builders = {
        'lightweight': build_lightweight_task,
        'document': build_document_query_task,
        'web_search': build_web_search_task,
        'multimodal': build_multimodal_task,
        'research': build_research_task,
        'chat': build_chat_task
    }
    
    return task_builders.get(agent_type, build_lightweight_task)

def create_task_for_query(query: str, agent_type: str, context: Dict = None) -> Task:
    """
    Create appropriate task for a query and agent type
    
    Args:
        query: User query
        agent_type: Type of agent to use
        context: Additional context
        
    Returns:
        Task instance
    """
    task_builder = get_task_builder(agent_type)
    
    if agent_type == 'document':
        return task_builder(query, context.get('document_context'))
    elif agent_type == 'web_search':
        return task_builder(query, context.get('search_context'))
    elif agent_type == 'multimodal':
        return task_builder(query, context.get('image_context'))
    elif agent_type == 'research':
        return task_builder(query, context.get('research_context'))
    elif agent_type == 'chat':
        return task_builder(query, context.get('chat_context'))
    else:
        return task_builder(query, context) 