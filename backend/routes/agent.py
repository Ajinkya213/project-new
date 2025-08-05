#!/usr/bin/env python3
"""
Simplified agent routes without authentication
"""

from flask import Blueprint, request, jsonify
from services.firebase_agent_service import firebase_agent_service
from services.firebase_auth_service import require_auth
from services.firebase_chat_service import firebase_chat_service
from services.document_service import DocumentService
from datetime import datetime

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/upload', methods=['POST'])
@require_auth
def upload_document():
    """Upload and process document with agent system"""
    try:
        user_info = request.user
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Process document with document service
        document_service = DocumentService()
        result = document_service.process_documents([file])
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': result.get('message', 'Document processed successfully'),
                'pages_processed': result.get('pages_processed', 0),
                'files_processed': result.get('files_processed', []),
                'embeddings_generated': result.get('embeddings_generated', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Document processing failed')
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@agent_bp.route('/query', methods=['POST'])
def process_query():
    """Process user query without authentication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        agent_type = data.get('agent_type')  # Optional, will auto-select if not provided
        session_id = data.get('session_id')  # Optional chat session ID
        context = data.get('context', {})  # Optional additional context
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Process query with agent service (no user authentication)
        from services.query_service import QueryService
        query_service = QueryService()
        result = query_service.process_query(query, agent_type, context)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),
                'agent_type': result.get('agent_type', 'unknown'),
                'processing_time': result.get('processing_time', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Query processing failed')
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Query processing failed: {str(e)}'
        }), 500

@agent_bp.route('/agents', methods=['GET'])
def get_available_agents():
    """Get available agents without authentication"""
    try:
        from agents.agents import get_agent_status
        agent_status = get_agent_status()
        available_agents = list(agent_status.keys())
        
        return jsonify({
            'success': True,
            'agents': available_agents
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get agents: {str(e)}'
        }), 500

@agent_bp.route('/agents/<agent_type>/status', methods=['GET'])
def get_agent_status(agent_type):
    """Get status of a specific agent without authentication"""
    try:
        from agents.agents import get_agent_status as get_agent_status_func
        
        status = get_agent_status_func(agent_type)
        
        return jsonify({
            'success': True,
            'agent_type': agent_type,
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get agent status: {str(e)}'
        }), 500

@agent_bp.route('/agents/status', methods=['GET'])
def get_all_agent_status():
    """Get status of all agents without authentication"""
    try:
        from agents.agents import get_agent_status as get_agent_status_func
        
        all_status = get_agent_status_func()
        
        return jsonify({
            'success': True,
            'agents': all_status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get agent status: {str(e)}'
        }), 500

@agent_bp.route('/history', methods=['GET'])
@require_auth
def get_user_agent_history():
    """Get user's agent interaction history"""
    try:
        user_info = request.user
        limit = request.args.get('limit', 10, type=int)
        
        history = firebase_agent_service.get_user_agent_history(user_info['uid'], limit)
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get history: {str(e)}'
        }), 500

@agent_bp.route('/analytics', methods=['GET'])
@require_auth
def get_agent_analytics():
    """Get agent usage analytics for the user"""
    try:
        user_info = request.user
        analytics = firebase_agent_service.get_agent_analytics(user_info['uid'])
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get analytics: {str(e)}'
        }), 500

@agent_bp.route('/chat/<session_id>/query', methods=['POST'])
@require_auth
def process_chat_query(session_id):
    """Process query in a specific chat session"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        agent_type = data.get('agent_type', 'chat')  # Default to chat agent
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Verify user has access to this chat session
        session = firebase_chat_service.get_chat_session(session_id, user_info['uid'])
        if not session:
            return jsonify({
                'success': False,
                'error': 'Chat session not found or access denied'
            }), 404
        
        # Process query with agent
        result = firebase_agent_service.process_user_query(
            user_id=user_info['uid'],
            query=query,
            agent_type=agent_type,
            session_id=session_id
        )
        
        if result.get('success'):
            # Add user message to chat
            firebase_chat_service.add_message(
                session_id=session_id,
                text=query,
                sender='user',
                user_id=user_info['uid']
            )
            
            # Add agent response to chat
            agent_response = result.get('response', '')
            firebase_chat_service.add_message(
                session_id=session_id,
                text=agent_response,
                sender='ai',
                user_id=user_info['uid']
            )
            
            return jsonify({
                'success': True,
                'result': result,
                'session_id': session_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Query processing failed')
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Chat query processing failed: {str(e)}'
        }), 500

@agent_bp.route('/auto-select', methods=['POST'])
def auto_select_agent():
    """Auto-select the best agent for a query without authentication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get agent selection reasoning
        from services.agent_selector import agent_selector
        reasoning = agent_selector.get_agent_reasoning(query)
        
        return jsonify({
            'success': True,
            'reasoning': reasoning
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Agent selection failed: {str(e)}'
        }), 500

@agent_bp.route('/auto-query', methods=['POST'])
def auto_query_agent():
    """Auto-select and process query with the best agent without authentication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Process query with agent service (no user authentication)
        from services.query_service import QueryService
        query_service = QueryService()
        
        # Auto-select agent
        agent_selection = query_service.auto_select_agent(query)
        selected_agent = agent_selection.get('agent_type', 'lightweight')
        
        # Process query with selected agent
        result = query_service.process_query(query, selected_agent, {})
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),
                'agent_type': selected_agent,
                'agent_selection': {
                    'selected_agent': selected_agent,
                    'confidence': agent_selection.get('confidence', 0.0),
                    'reasoning': agent_selection.get('reason', 'Auto-selected based on query content')
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Query processing failed')
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Auto query failed: {str(e)}'
        }), 500

@agent_bp.route('/health', methods=['GET'])
def agent_health_check():
    """Health check for agent system"""
    try:
        from agents.agents import get_agent_status as get_agent_status_func
        
        agent_status = get_agent_status_func()
        available_agents = list(agent_status.keys())
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'available_agents': available_agents,
            'total_agents': len(available_agents),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500 

@agent_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get documents without authentication"""
    try:
        # For now, return empty document list
        return jsonify({
            'success': True,
            'documents': [],
            'total_documents': 0
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get documents: {str(e)}'
        }), 500

@agent_bp.route('/documents/analytics', methods=['GET'])
def get_document_analytics():
    """Get document analytics without authentication"""
    try:
        # For now, return empty analytics
        return jsonify({
            'success': True,
            'analytics': {
                'total_documents': 0,
                'total_pages': 0,
                'document_types': {},
                'embeddings_generated': 0,
                'recent_uploads': []
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get analytics: {str(e)}'
        }), 500 