#!/usr/bin/env python3
"""
Agent routes for API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import query_service, lightweight_agent, document_service
import os
from werkzeug.utils import secure_filename
from config.settings import DevelopmentConfig

# Create blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/agent')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in DevelopmentConfig.ALLOWED_EXTENSIONS

@agent_bp.route('/health', methods=['GET'])
def health_check():
    """Check agent service health"""
    try:
        health = query_service.health_check()
        return jsonify(health), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@agent_bp.route('/test', methods=['POST'])
def test_agent():
    """Test agent functionality"""
    try:
        data = request.get_json()
        query = data.get('query', 'Hello')
        
        # Test lightweight agent
        response = lightweight_agent.process_query(query)
        
        return jsonify({
            'success': True,
            'result': {
                'response': response,
                'agent_type': 'lightweight'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/query', methods=['POST'])
@jwt_required()
def query_agent():
    """Query agent with authentication"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        agent_type = data.get('agent_type', 'lightweight')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        result = query_service.process_query(query, agent_type, context)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/auto-query', methods=['POST'])
@jwt_required()
def auto_query_agent():
    """Query with automatic agent selection"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Auto-select the best agent
        agent_selection = query_service.auto_select_agent(query)
        selected_agent = agent_selection['selected_agent']
        
        # Process the query with the selected agent
        result = query_service.process_query(query, selected_agent)
        
        # Add agent selection info to the result
        result['agent_selection'] = agent_selection
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload and process documents"""
    try:
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
        
        if file and allowed_file(file.filename):
            # Process the document
            result = document_service.process_documents([file])
            
            if result['status'] == 'success':
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'pages_processed': result.get('pages_processed', 0)
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result['message']
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(DevelopmentConfig.ALLOWED_EXTENSIONS)}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@agent_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get information about indexed documents"""
    try:
        info = document_service.get_document_info()
        return jsonify(info), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/agents', methods=['GET'])
def list_agents():
    """List available agents"""
    try:
        agents = query_service.get_available_agents()
        return jsonify({
            'success': True,
            'agents': agents
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/status', methods=['GET'])
def get_agent_status():
    """Get agent status and statistics"""
    try:
        agent_type = request.args.get('agent_type')
        status = query_service.get_agent_status(agent_type)
        return jsonify({
            'success': True,
            'status': status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_bp.route('/stats', methods=['GET'])
def get_agent_stats():
    """Get detailed agent statistics"""
    try:
        agent_type = request.args.get('agent_type')
        status = query_service.get_agent_status(agent_type)
        
        # Add additional statistics
        stats = {
            'agent_status': status,
            'performance_metrics': {
                'total_queries': sum(s.get('total_queries', 0) for s in status.values()) if isinstance(status, dict) else status.get('total_queries', 0),
                'success_rate': sum(s.get('success_rate', 0) for s in status.values()) / len(status) if isinstance(status, dict) and len(status) > 0 else status.get('success_rate', 0),
                'average_response_time': sum(s.get('average_response_time', 0) for s in status.values()) / len(status) if isinstance(status, dict) and len(status) > 0 else status.get('average_response_time', 0)
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 