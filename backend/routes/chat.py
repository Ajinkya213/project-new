from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db
from models.user import User
from models.chat import ChatSession, Message
from utils.auth_utils import get_current_user, require_auth, validate_user_input, sanitize_input
from utils.validators import MessageValidator, SessionValidator, PaginationValidator
from datetime import datetime

# Create Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# ==================== CHAT SESSIONS ====================

@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Get title from request or use default
        title = data.get('title', 'New Chat')
        title = sanitize_input(title)
        
        # Validate title
        is_valid, error_msg = SessionValidator.validate_title(title)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Create session
        session = ChatSession(title=title, user_id=user.id)
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Chat session created successfully',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create session', 'details': str(e)}), 500

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all chat sessions for the current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination
        is_valid, error_msg, pagination_params = PaginationValidator.validate_pagination_params(page, per_page)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Get sessions with pagination
        sessions_query = ChatSession.query.filter_by(user_id=user.id, is_active=True)
        sessions = sessions_query.order_by(ChatSession.updated_at.desc()).paginate(
            page=pagination_params['page'],
            per_page=pagination_params['per_page'],
            error_out=False
        )
        
        sessions_list = [session.to_dict() for session in sessions.items]
        
        return jsonify({
            'sessions': sessions_list,
            'pagination': {
                'page': sessions.page,
                'per_page': sessions.per_page,
                'total': sessions.total,
                'pages': sessions.pages,
                'has_next': sessions.has_next,
                'has_prev': sessions.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get sessions', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get a specific chat session with messages"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'session': session.to_dict_with_messages()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get session', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    """Update chat session title"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update title
        if 'title' in data:
            new_title = sanitize_input(data['title'])
            is_valid, error_msg = SessionValidator.validate_title(new_title)
            
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            session.update_title(new_title)
            db.session.commit()
        
        return jsonify({
            'message': 'Session updated successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update session', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """Delete a chat session (soft delete)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Soft delete session
        session.deactivate()
        db.session.commit()
        
        return jsonify({
            'message': 'Session deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete session', 'details': str(e)}), 500

# ==================== MESSAGES ====================

@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    """Send a message to a chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['text', 'sender']
        validation_errors = validate_user_input(data, required_fields)
        
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        text = sanitize_input(data['text'])
        sender = data['sender']
        
        # Validate message
        is_valid, error_msg = MessageValidator.validate_message(text)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate sender
        if sender not in ['user', 'ai']:
            return jsonify({'error': 'Sender must be "user" or "ai"'}), 400
        
        # Create message
        message = Message(text=text, sender=sender, session_id=session_id)
        db.session.add(message)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(session_id):
    """Get all messages for a chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Validate pagination
        is_valid, error_msg, pagination_params = PaginationValidator.validate_pagination_params(page, per_page)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Get messages with pagination
        messages_query = Message.query.filter_by(session_id=session_id, is_deleted=False)
        messages = messages_query.order_by(Message.created_at.asc()).paginate(
            page=pagination_params['page'],
            per_page=pagination_params['per_page'],
            error_out=False
        )
        
        messages_list = [message.to_dict() for message in messages.items]
        
        return jsonify({
            'messages': messages_list,
            'pagination': {
                'page': messages.page,
                'per_page': messages.per_page,
                'total': messages.total,
                'pages': messages.pages,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get messages', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def update_message(session_id, message_id):
    """Update a specific message"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Check if message belongs to session
        if message.session_id != session_id:
            return jsonify({'error': 'Message does not belong to this session'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update text
        if 'text' in data:
            new_text = sanitize_input(data['text'])
            is_valid, error_msg = MessageValidator.validate_message(new_text)
            
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            message.update_text(new_text)
            db.session.commit()
        
        return jsonify({
            'message': 'Message updated successfully',
            'message_data': message.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update message', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(session_id, message_id):
    """Delete a specific message (soft delete)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Check if message belongs to session
        if message.session_id != session_id:
            return jsonify({'error': 'Message does not belong to this session'}), 400
        
        # Soft delete message
        message.soft_delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Message deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete message', 'details': str(e)}), 500

@chat_bp.route('/sessions/<int:session_id>/messages', methods=['DELETE'])
@jwt_required()
def clear_messages(session_id):
    """Clear all messages in a session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check ownership
        if session.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Soft delete all messages
        messages = Message.query.filter_by(session_id=session_id, is_deleted=False).all()
        for message in messages:
            message.soft_delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'All messages cleared successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to clear messages', 'details': str(e)}), 500 