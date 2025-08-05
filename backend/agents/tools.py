"""
Tools Integration - Strategy Pattern for Different Retrieval Methods
Implements different tools for different retrieval methods and agent capabilities
"""

from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
import requests
import json
import os
from datetime import datetime

# Import core components
from core.rag_singleton import get_rag

# Available tools registry
_available_tools = {}

def get_available_tools() -> List[Dict[str, Any]]:
    """
    Get list of available tools with their metadata
    """
    return [
        {
            'name': 'web_search',
            'description': 'Search the web for current information',
            'category': 'web_search',
            'agent_types': ['web_search', 'research']
        },
        {
            'name': 'document_retrieval',
            'description': 'Retrieve information from uploaded documents',
            'category': 'document',
            'agent_types': ['document', 'multimodal']
        },
        {
            'name': 'image_analysis',
            'description': 'Analyze images and visual content',
            'category': 'multimodal',
            'agent_types': ['multimodal']
        },
        {
            'name': 'text_analysis',
            'description': 'Analyze and process text content',
            'category': 'basic',
            'agent_types': ['lightweight', 'document']
        },
        {
            'name': 'data_calculation',
            'description': 'Perform calculations and data analysis',
            'category': 'utility',
            'agent_types': ['lightweight', 'research']
        }
    ]

def get_tool_by_name(tool_name: str) -> Optional[BaseTool]:
    """
    Get tool instance by name
    """
    if tool_name == 'web_search':
        return WebSearchTool()
    elif tool_name == 'document_retrieval':
        return DocumentRetrievalTool()
    elif tool_name == 'image_analysis':
        return ImageAnalysisTool()
    elif tool_name == 'text_analysis':
        return TextAnalysisTool()
    elif tool_name == 'data_calculation':
        return DataCalculationTool()
    else:
        return None

class WebSearchTool(BaseTool):
    """
    Web Search Tool for retrieving current information
    """
    
    name: str = "web_search"
    description: str = "Search the web for current information and news"
    
    def _run(self, query: str) -> str:
        """
        Execute web search
        """
        try:
            # Simple web search implementation
            # In production, you'd use a proper search API
            search_results = self._perform_web_search(query)
            return f"Web search results for '{query}': {search_results}"
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    def _perform_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search (placeholder implementation)
        """
        # This would be replaced with actual search API
        return [
            {
                'title': f'Search result for {query}',
                'url': 'https://example.com',
                'snippet': f'Information about {query}'
            }
        ]

class DocumentRetrievalTool(BaseTool):
    """
    Document Retrieval Tool for accessing uploaded documents
    """
    
    name: str = "document_retrieval"
    description: str = "Retrieve information from uploaded documents"
    
    def _run(self, query: str) -> str:
        """
        Execute document retrieval
        """
        try:
            rag_instance = get_rag()
            results = rag_instance.search(query, limit=3)
            
            if results and results.get('results'):
                return f"Document search results for '{query}': {results['results']}"
            else:
                return f"No relevant documents found for '{query}'"
        except Exception as e:
            return f"Document retrieval failed: {str(e)}"

class ImageAnalysisTool(BaseTool):
    """
    Image Analysis Tool for processing visual content
    """
    
    name: str = "image_analysis"
    description: str = "Analyze images and extract visual information"
    
    def _run(self, image_path: str) -> str:
        """
        Execute image analysis
        """
        try:
            # Placeholder for image analysis
            # In production, you'd use a vision model
            return f"Image analysis for '{image_path}': Visual content detected"
        except Exception as e:
            return f"Image analysis failed: {str(e)}"

class TextAnalysisTool(BaseTool):
    """
    Text Analysis Tool for processing text content
    """
    
    name: str = "text_analysis"
    description: str = "Analyze and process text content"
    
    def _run(self, text: str) -> str:
        """
        Execute text analysis
        """
        try:
            # Simple text analysis
            word_count = len(text.split())
            char_count = len(text)
            
            return f"Text analysis: {word_count} words, {char_count} characters"
        except Exception as e:
            return f"Text analysis failed: {str(e)}"

class DataCalculationTool(BaseTool):
    """
    Data Calculation Tool for mathematical operations
    """
    
    name: str = "data_calculation"
    description: str = "Perform calculations and data analysis"
    
    def _run(self, expression: str) -> str:
        """
        Execute calculation
        """
        try:
            # Safe evaluation of mathematical expressions
            allowed_chars = set('0123456789+-*/(). ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"Calculation result: {result}"
            else:
                return "Invalid expression for calculation"
        except Exception as e:
            return f"Calculation failed: {str(e)}"

def register_tool(tool_name: str, tool_instance: BaseTool):
    """
    Register a custom tool
    """
    _available_tools[tool_name] = tool_instance

def get_tool_categories() -> Dict[str, List[str]]:
    """
    Get tools organized by category
    """
    tools = get_available_tools()
    categories = {}
    
    for tool in tools:
        category = tool.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append(tool['name'])
    
    return categories

def get_tools_for_agent(agent_type: str) -> List[BaseTool]:
    """
    Get tools appropriate for a specific agent type
    """
    tools = get_available_tools()
    agent_tools = []
    
    for tool in tools:
        if agent_type in tool.get('agent_types', []):
            tool_instance = get_tool_by_name(tool['name'])
            if tool_instance:
                agent_tools.append(tool_instance)
    
    return agent_tools

def validate_tool_usage(tool_name: str, agent_type: str) -> bool:
    """
    Validate if a tool can be used by an agent type
    """
    tools = get_available_tools()
    
    for tool in tools:
        if tool['name'] == tool_name:
            return agent_type in tool.get('agent_types', [])
    
    return False

def get_tool_metadata(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific tool
    """
    tools = get_available_tools()
    
    for tool in tools:
        if tool['name'] == tool_name:
            return tool
    
    return None 