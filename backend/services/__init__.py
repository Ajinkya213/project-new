"""
Services package initialization - Cleaned Structure

Essential Services:
- query_service: Main query processing with agent selection
- document_service: Document processing and indexing
- lightweight_agent: Fast query processing with Gemini
- agent_selector: Intelligent agent selection
"""

from .query_service import QueryService
from .lightweight_agent import LightweightAgent, lightweight_agent
from .document_service import DocumentService, document_service
from .agent_selector import AgentSelector

__all__ = [
    'QueryService',
    'LightweightAgent',
    'lightweight_agent',
    'DocumentService',
    'document_service',
    'AgentSelector'
] 