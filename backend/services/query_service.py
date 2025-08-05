"""
Service Layer - Business logic for query processing and agent orchestration
Implements the complete query processing flow with agent selection and RAG integration
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import core components
from core.rag_singleton import get_rag
from core.unified_agent import UnifiedAgent

# Import agent components
from agents.agents import get_agent_status, get_agent
from agents.tasks import build_task, build_document_processing_task
from agents.tools import get_available_tools

# Import services
from services.agent_selector import AgentSelector
from services.document_service import DocumentService

class QueryService:
    """
    Enhanced query service with complete business logic
    Handles agent orchestration, RAG integration, and response generation
    """
    
    def __init__(self):
        self.rag_instance = get_rag()
        self.agent_selector = AgentSelector()
        self.document_service = DocumentService()
        self.unified_agent = UnifiedAgent()
    
    def process_query(self, query: str, agent_type: str = None, context: Dict = None) -> Dict[str, Any]:
        """
        Process query with agent orchestration and RAG integration
        
        Args:
            query: User query text
            agent_type: Specific agent to use (optional, auto-selected if not provided)
            context: Additional context for processing
            
        Returns:
            Dict with processing results
        """
        start_time = time.time()
        
        try:
            # Auto-select agent if not specified
            if not agent_type:
                agent_selection = self.agent_selector.select_agent(query)
                agent_type = agent_selection.get('agent_type', 'lightweight')
                confidence = agent_selection.get('confidence', 0.0)
                reasoning = agent_selection.get('reasoning', 'Auto-selected based on query content')
            else:
                confidence = 1.0
                reasoning = 'Manually specified'
            
            # Get agent instance
            agent = get_agent(agent_type)
            if not agent:
                return {
                    'status': 'error',
                    'message': f'Agent type "{agent_type}" not available'
                }
            
            # Process query based on agent type
            if agent_type == 'document':
                result = self._process_document_query(query, context)
            elif agent_type == 'web_search':
                result = self._process_web_query(query, context)
            elif agent_type == 'multimodal':
                result = self._process_multimodal_query(query, context)
            else:
                result = self._process_general_query(query, agent_type, context)
            
            # Add metadata
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            result['agent_type'] = agent_type
            result['confidence'] = confidence
            result['reasoning'] = reasoning
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Query processing failed: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    def _process_document_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process document-specific queries using RAG system
        """
        try:
            # Search documents using RAG
            search_result = self.rag_instance.search(query, limit=5)
            
            if not search_result or not search_result.get('results'):
                return {
                    'status': 'success',
                    'response': 'I couldn\'t find any relevant information in the uploaded documents.',
                    'sources': [],
                    'document_matches': 0
                }
            
            # Extract relevant information
            results = search_result.get('results', [])
            sources = []
            document_matches = []
            
            for result in results:
                if result.get('content'):
                    sources.append(result['content'])
                    document_matches.append({
                        'filename': result.get('metadata', {}).get('filename', 'Unknown'),
                        'page': result.get('metadata', {}).get('page', 1),
                        'content': result['content'][:200] + '...' if len(result['content']) > 200 else result['content']
                    })
            
            # Generate response using unified agent
            response = self.unified_agent.generate_response(
                query=query,
                context=context or {},
                sources=sources,
                agent_type='document'
            )
            
            return {
                'status': 'success',
                'response': response,
                'sources': sources,
                'document_matches': document_matches,
                'documents_found': len(results)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Document query processing failed: {str(e)}'
            }
    
    def _process_web_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process web search queries
        """
        try:
            # Use web search agent
            web_agent = get_agent('web_search')
            if not web_agent:
                return {
                    'status': 'error',
                    'message': 'Web search agent not available'
                }
            
            # Build web search task
            task = build_task(
                description=f"Search the web for: {query}",
                agent=web_agent,
                context=context or {}
            )
            
            # Execute task
            result = task.execute()
            
            return {
                'status': 'success',
                'response': result.get('output', 'No web search results found'),
                'web_matches': result.get('web_results', []),
                'sources': result.get('sources', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Web query processing failed: {str(e)}'
            }
    
    def _process_multimodal_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process multimodal queries (text + images)
        """
        try:
            # Use multimodal agent
            multimodal_agent = get_agent('multimodal')
            if not multimodal_agent:
                return {
                    'status': 'error',
                    'message': 'Multimodal agent not available'
                }
            
            # Build multimodal task
            task = build_task(
                description=f"Process multimodal query: {query}",
                agent=multimodal_agent,
                context=context or {}
            )
            
            # Execute task
            result = task.execute()
            
            return {
                'status': 'success',
                'response': result.get('output', 'No multimodal results found'),
                'images_processed': result.get('images_processed', 0),
                'sources': result.get('sources', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Multimodal query processing failed: {str(e)}'
            }
    
    def _process_general_query(self, query: str, agent_type: str, context: Dict = None) -> Dict[str, Any]:
        """
        Process general queries with specified agent
        """
        try:
            # Get agent
            agent = get_agent(agent_type)
            if not agent:
                return {
                    'status': 'error',
                    'message': f'Agent type "{agent_type}" not available'
                }
            
            # Build task
            task = build_task(
                description=f"Process query: {query}",
                agent=agent,
                context=context or {}
            )
            
            # Execute task
            result = task.execute()
            
            return {
                'status': 'success',
                'response': result.get('output', 'No response generated'),
                'sources': result.get('sources', []),
                'tools_used': result.get('tools_used', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'General query processing failed: {str(e)}'
            }
    
    def auto_select_agent(self, query: str) -> Dict[str, Any]:
        """
        Auto-select the best agent for a given query
        """
        try:
            return self.agent_selector.select_agent(query)
        except Exception as e:
            return {
                'agent_type': 'lightweight',
                'confidence': 0.0,
                'reasoning': f'Agent selection failed: {str(e)}'
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all available agents
        """
        try:
            return get_agent_status()
        except Exception as e:
            return {
                'error': f'Failed to get agent status: {str(e)}'
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools for agents
        """
        try:
            return get_available_tools()
        except Exception as e:
            return [] 