"""
Agent Layer - AI agent orchestration and management
Implements the agent system with CrewAI integration and tool management
"""

from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import asyncio
import time
from datetime import datetime

# Import tools
from agents.tools import get_available_tools, get_tool_by_name

# Agent status tracking
_agent_status = {
    'lightweight': {'status': 'online', 'last_used': None},
    'document': {'status': 'online', 'last_used': None},
    'web_search': {'status': 'online', 'last_used': None},
    'multimodal': {'status': 'online', 'last_used': None},
    'research': {'status': 'online', 'last_used': None}
}

def get_agent_status(agent_type: str = None) -> Dict[str, Any]:
    """
    Get status of agents
    """
    if agent_type:
        return _agent_status.get(agent_type, {'status': 'unknown'})
    return _agent_status

def update_agent_status(agent_type: str, status: str):
    """
    Update agent status
    """
    if agent_type in _agent_status:
        _agent_status[agent_type]['status'] = status
        _agent_status[agent_type]['last_used'] = datetime.now().isoformat()

def get_agent(agent_type: str) -> Optional[Agent]:
    """
    Get agent instance by type
    """
    try:
        if agent_type == 'lightweight':
            return create_lightweight_agent()
        elif agent_type == 'document':
            return create_document_agent()
        elif agent_type == 'web_search':
            return create_web_search_agent()
        elif agent_type == 'multimodal':
            return create_multimodal_agent()
        elif agent_type == 'research':
            return create_research_agent()
        else:
            print(f"[WARNING] Unknown agent type: {agent_type}")
            return create_lightweight_agent()
    except Exception as e:
        print(f"[ERROR] Failed to create agent {agent_type}: {e}")
        return None

def create_lightweight_agent() -> Agent:
    """
    Create lightweight agent for fast responses
    """
    tools = get_available_tools()
    lightweight_tools = [tool for tool in tools if tool.get('category') in ['basic', 'utility']]
    
    return Agent(
        role="Lightweight Assistant",
        goal="Provide quick, accurate responses to general queries",
        backstory="You are a helpful AI assistant focused on providing fast and accurate responses to user queries.",
        tools=[get_tool_by_name(tool['name']) for tool in lightweight_tools if get_tool_by_name(tool['name'])],
        verbose=True,
        allow_delegation=False
    )

def create_document_agent() -> Agent:
    """
    Create document processing agent
    """
    tools = get_available_tools()
    document_tools = [tool for tool in tools if tool.get('category') in ['document', 'search']]
    
    return Agent(
        role="Document Analysis Specialist",
        goal="Analyze and extract information from uploaded documents",
        backstory="You are an expert at analyzing documents, extracting key information, and providing insights based on document content.",
        tools=[get_tool_by_name(tool['name']) for tool in document_tools if get_tool_by_name(tool['name'])],
        verbose=True,
        allow_delegation=False
    )

def create_web_search_agent() -> Agent:
    """
    Create web search agent
    """
    tools = get_available_tools()
    web_tools = [tool for tool in tools if tool.get('category') in ['web_search', 'research']]
    
    return Agent(
        role="Web Research Specialist",
        goal="Search the web for current information and provide comprehensive research results",
        backstory="You are an expert at searching the web for current information, analyzing search results, and providing comprehensive answers.",
        tools=[get_tool_by_name(tool['name']) for tool in web_tools if get_tool_by_name(tool['name'])],
        verbose=True,
        allow_delegation=False
    )

def create_multimodal_agent() -> Agent:
    """
    Create multimodal agent for text and image processing
    """
    tools = get_available_tools()
    multimodal_tools = [tool for tool in tools if tool.get('category') in ['multimodal', 'image', 'vision']]
    
    return Agent(
        role="Multimodal Analysis Specialist",
        goal="Process and analyze both text and image content",
        backstory="You are an expert at analyzing both text and visual content, providing insights from images, charts, and documents.",
        tools=[get_tool_by_name(tool['name']) for tool in multimodal_tools if get_tool_by_name(tool['name'])],
        verbose=True,
        allow_delegation=False
    )

def create_research_agent() -> Agent:
    """
    Create research agent for comprehensive analysis
    """
    tools = get_available_tools()
    research_tools = [tool for tool in tools if tool.get('category') in ['research', 'analysis', 'web_search']]
    
    return Agent(
        role="Research Analyst",
        goal="Conduct comprehensive research and provide detailed analysis",
        backstory="You are an expert researcher who can conduct thorough analysis, gather information from multiple sources, and provide detailed insights.",
        tools=[get_tool_by_name(tool['name']) for tool in research_tools if get_tool_by_name(tool['name'])],
        verbose=True,
        allow_delegation=False
    )

def execute_agent_task(agent: Agent, task_description: str, context: Dict = None) -> Dict[str, Any]:
    """
    Execute a task with an agent
    """
    try:
        start_time = time.time()
        
        # Create task
        task = Task(
            description=task_description,
            agent=agent,
            context=context or {}
        )
        
        # Create crew with single agent
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        # Execute task
        result = crew.kickoff()
        
        processing_time = time.time() - start_time
        
        return {
            'status': 'success',
            'output': result,
            'processing_time': processing_time,
            'agent_type': agent.role,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'processing_time': time.time() - start_time if 'start_time' in locals() else 0,
            'timestamp': datetime.now().isoformat()
        }

def get_agent_capabilities() -> Dict[str, List[str]]:
    """
    Get capabilities of each agent type
    """
    return {
        'lightweight': [
            'General conversation',
            'Basic information retrieval',
            'Fast responses',
            'Simple calculations'
        ],
        'document': [
            'Document analysis',
            'Text extraction',
            'Content summarization',
            'Document search'
        ],
        'web_search': [
            'Web search',
            'Current information retrieval',
            'News and updates',
            'Real-time data'
        ],
        'multimodal': [
            'Image analysis',
            'Visual content processing',
            'Chart and graph interpretation',
            'Document image analysis'
        ],
        'research': [
            'Comprehensive research',
            'Multi-source analysis',
            'Detailed reporting',
            'Academic research'
        ]
    }

def get_agent_recommendations(query: str) -> Dict[str, float]:
    """
    Get agent recommendations based on query content
    """
    query_lower = query.lower()
    recommendations = {}
    
    # Document-related keywords
    doc_keywords = ['document', 'pdf', 'file', 'upload', 'content', 'text', 'page', 'section']
    if any(keyword in query_lower for keyword in doc_keywords):
        recommendations['document'] = 0.9
    
    # Web search keywords
    web_keywords = ['latest', 'news', 'current', 'today', 'weather', 'stock', 'price', 'what is', 'how to']
    if any(keyword in query_lower for keyword in web_keywords):
        recommendations['web_search'] = 0.8
    
    # Multimodal keywords
    multimodal_keywords = ['image', 'picture', 'photo', 'chart', 'graph', 'visual', 'see', 'show']
    if any(keyword in query_lower for keyword in multimodal_keywords):
        recommendations['multimodal'] = 0.9
    
    # Research keywords
    research_keywords = ['research', 'study', 'analysis', 'comprehensive', 'detailed', 'investigate']
    if any(keyword in query_lower for keyword in research_keywords):
        recommendations['research'] = 0.8
    
    # Default to lightweight if no specific recommendations
    if not recommendations:
        recommendations['lightweight'] = 0.7
    
    return recommendations 