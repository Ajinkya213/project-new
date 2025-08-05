from flask import Blueprint, request, jsonify
from services.firebase_auth_service import firebase_auth_service, require_auth
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Sign up new user with Firebase Auth"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Create user in Firebase Auth
        user = firebase_auth_service.create_user(email, password, name)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Failed to create user. Email might already be in use.'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'uid': user['uid'],
                'email': user['email'],
                'name': user['name'],
                'email_verified': user['email_verified']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Signup failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - returns user info for Firebase Auth"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Note: Firebase Auth handles login on the frontend
        # This endpoint can be used for additional server-side validation if needed
        return jsonify({
            'success': True,
            'message': 'Login successful. Use Firebase Auth on frontend.',
            'auth_method': 'firebase'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({
                'success': False,
                'error': 'ID token is required'
            }), 400
        
        # Verify token with Firebase
        user_info = firebase_auth_service.verify_token(id_token)
        
        if not user_info:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        return jsonify({
            'success': True,
            'user': user_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Token verification failed: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user_info = request.user
        
        # Get additional user data from Firestore if needed
        user_data = firebase_auth_service.get_user(user_info['uid'])
        
        return jsonify({
            'success': True,
            'user': user_data or user_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get profile: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        user_info = request.user
        data = request.get_json()
        
        update_data = {}
        if 'name' in data:
            update_data['display_name'] = data['name']
        
        if not update_data:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        # Update user in Firebase Auth
        updated_user = firebase_auth_service.update_user(user_info['uid'], **update_data)
        
        if not updated_user:
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
        
        return jsonify({
            'success': True,
            'user': updated_user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update profile: {str(e)}'
        }), 500

@auth_bp.route('/delete-account', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete user account"""
    try:
        user_info = request.user
        
        # Delete user from Firebase Auth
        success = firebase_auth_service.delete_user(user_info['uid'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete account'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete account: {str(e)}'
        }), 500 