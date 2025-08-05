from flask import Blueprint, request, jsonify
from services.firebase_chat_service import firebase_chat_service
from services.firebase_auth_service import require_auth

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/sessions', methods=['GET'])
@require_auth
def get_chat_sessions():
    """Get all chat sessions for the authenticated user"""
    try:
        user_info = request.user
        sessions = firebase_chat_service.get_chat_sessions(user_info['uid'])
        
        return jsonify({
            'success': True,
            'sessions': sessions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get chat sessions: {str(e)}'
        }), 500

@chat_bp.route('/sessions', methods=['POST'])
@require_auth
def create_chat_session():
    """Create a new chat session"""
    try:
        user_info = request.user
        data = request.get_json()
        title = data.get('title', 'New Chat') if data else 'New Chat'
        
        session = firebase_chat_service.create_chat_session(user_info['uid'], title)
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Failed to create chat session'
            }), 500
        
        return jsonify({
            'success': True,
            'session': session
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create chat session: {str(e)}'
        }), 500

@chat_bp.route('/sessions/<session_id>', methods=['GET'])
@require_auth
def get_chat_session(session_id):
    """Get a specific chat session with messages"""
    try:
        user_info = request.user
        session = firebase_chat_service.get_chat_session(session_id, user_info['uid'])
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Chat session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session': session
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get chat session: {str(e)}'
        }), 500

@chat_bp.route('/sessions/<session_id>', methods=['PUT'])
@require_auth
def update_chat_session(session_id):
    """Update chat session title"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        # Verify session exists and user has access
        session = firebase_chat_service.get_chat_session(session_id, user_info['uid'])
        if not session:
            return jsonify({
                'success': False,
                'error': 'Chat session not found'
            }), 404
        
        success = firebase_chat_service.update_chat_session(session_id, title=data['title'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update chat session'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Chat session updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update chat session: {str(e)}'
        }), 500

@chat_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
def delete_chat_session(session_id):
    """Delete chat session"""
    try:
        user_info = request.user
        success = firebase_chat_service.delete_chat_session(session_id, user_info['uid'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete chat session'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Chat session deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete chat session: {str(e)}'
        }), 500

@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@require_auth
def add_message(session_id):
    """Add a message to a chat session"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        text = data.get('text', '').strip()
        sender = data.get('sender', 'user')  # 'user' or 'ai'
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Message text is required'
            }), 400
        
        if sender not in ['user', 'ai']:
            return jsonify({
                'success': False,
                'error': 'Sender must be "user" or "ai"'
            }), 400
        
        message = firebase_chat_service.add_message(session_id, text, sender, user_info['uid'])
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Failed to add message'
            }), 500
        
        return jsonify({
            'success': True,
            'message': message
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to add message: {str(e)}'
        }), 500

@chat_bp.route('/messages/<message_id>', methods=['PUT'])
@require_auth
def update_message(message_id):
    """Update a message"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Message text is required'
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Message text cannot be empty'
            }), 400
        
        success = firebase_chat_service.update_message(message_id, text, user_info['uid'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update message'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Message updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update message: {str(e)}'
        }), 500

@chat_bp.route('/messages/<message_id>', methods=['DELETE'])
@require_auth
def delete_message(message_id):
    """Delete a message"""
    try:
        user_info = request.user
        success = firebase_chat_service.delete_message(message_id, user_info['uid'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete message'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete message: {str(e)}'
        }), 500 