"""
API Layer - REST endpoints for document processing and query handling
Implements the complete dataflow from upload to query processing
"""

from flask import Blueprint, request, jsonify
from werkzeug.datastructures import FileStorage
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime

# Import service layer
from services.query_service import QueryService
from services.document_service import DocumentService
from services.agent_selector import AgentSelector

# Import core components
from core.rag_singleton import get_rag
from core.unified_agent import UnifiedAgent

# Import agent components
from agents.agents import get_agent_status
from agents.tasks import build_task, build_document_processing_task
from agents.tools import get_available_tools

api_bp = Blueprint('api', __name__)

@api_bp.route("/upload/", methods=['POST'])
async def upload():
    """
    Document Upload Endpoint
    Handles PDF upload, conversion, and indexing
    """
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        # Process documents using service layer
        result = await process_documents(files)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@api_bp.route("/query/", methods=['POST'])
async def query():
    """
    Query Processing Endpoint
    Handles user queries with agent orchestration
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query_text = data.get('query', '').strip()
        agent_type = data.get('agent_type')  # Optional auto-selection
        context = data.get('context', {})
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Process query using service layer
        result = await process_query(query_text, agent_type, context)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Query processing failed: {str(e)}'
        }), 500

@api_bp.route("/agents/", methods=['GET'])
def get_agents():
    """
    Get available agents and their status
    """
    try:
        agent_status = get_agent_status()
        
        return jsonify({
            'success': True,
            'agents': agent_status,
            'total_agents': len(agent_status)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get agents: {str(e)}'
        }), 500

@api_bp.route("/tools/", methods=['GET'])
def get_tools():
    """
    Get available tools for agents
    """
    try:
        tools = get_available_tools()
        
        return jsonify({
            'success': True,
            'tools': tools,
            'total_tools': len(tools)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get tools: {str(e)}'
        }), 500

@api_bp.route("/documents/", methods=['GET'])
def get_documents():
    """
    Get indexed documents information
    """
    try:
        rag_instance = get_rag()
        documents = rag_instance.get_document_info()
        
        return jsonify({
            'success': True,
            'documents': documents
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get documents: {str(e)}'
        }), 500

@api_bp.route("/health/", methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    try:
        # Check core components
        rag_instance = get_rag()
        agent_status = get_agent_status()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'components': {
                'rag_system': 'operational',
                'agents': len(agent_status),
                'timestamp': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Service Layer Functions
async def process_documents(files: List[FileStorage]) -> Dict[str, Any]:
    """
    Process documents using CrewAI agents for consistent logic
    """
    try:
        all_data = []
        processed_files = []
        
        # Convert PDFs to data
        document_service = DocumentService()
        result = document_service.process_documents(files)
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'message': result.get('message', 'Documents processed successfully'),
                'pages_processed': result.get('pages_processed', 0),
                'files_processed': result.get('files_processed', []),
                'embeddings_generated': result.get('embeddings_generated', 0)
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Document processing failed')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Document processing failed: {str(e)}'
        }

async def process_query(query: str, agent_type: str = None, context: Dict = None) -> Dict[str, Any]:
    """
    Process query with agent orchestration
    """
    try:
        # Auto-select agent if not specified
        if not agent_type:
            agent_selector = AgentSelector()
            agent_selection = agent_selector.select_agent(query)
            agent_type = agent_selection.get('agent_type', 'lightweight')
        
        # Process query with selected agent
        query_service = QueryService()
        result = query_service.process_query(query, agent_type, context or {})
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'response': result.get('response', 'No response generated'),
                'agent_type': agent_type,
                'processing_time': result.get('processing_time', 0),
                'sources': result.get('sources', []),
                'confidence': result.get('confidence', 0.0)
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Query processing failed')
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Query processing failed: {str(e)}'
        } 