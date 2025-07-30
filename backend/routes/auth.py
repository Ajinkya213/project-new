from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import db
from models.user import User
from utils.auth_utils import generate_tokens, get_current_user, validate_user_input, sanitize_input
from utils.validators import UserValidator
import uuid

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        validation_errors = validate_user_input(data, required_fields)
        
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Sanitize inputs
        username = sanitize_input(data['username'])
        email = sanitize_input(data['email'])
        password = data['password']
        
        # Validate username
        is_valid_username, username_error = UserValidator.validate_username(username)
        if not is_valid_username:
            return jsonify({'error': username_error}), 400
        
        # Validate email
        is_valid_email, email_error = UserValidator.validate_email(email)
        if not is_valid_email:
            return jsonify({'error': email_error}), 400
        
        # Validate password
        is_valid_password, password_error = UserValidator.validate_password(password)
        if not is_valid_password:
            return jsonify({'error': password_error}), 400
        
        # Check if username already exists
        if User.find_by_username(username):
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if User.find_by_email(email):
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'tokens': tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['username', 'password']
        validation_errors = validate_user_input(data, required_fields)
        
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        username = sanitize_input(data['username'])
        password = data['password']
        
        # Find user by username or email
        user = User.find_by_username(username)
        if not user:
            user = User.find_by_email(username)
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check password
        if not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate new tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    try:
        # In a real application, you might want to blacklist the token
        # For now, we'll just return a success message
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict_with_sessions()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update username if provided
        if 'username' in data:
            new_username = sanitize_input(data['username'])
            is_valid, error_msg = UserValidator.validate_username(new_username)
            
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            # Check if username is already taken by another user
            existing_user = User.find_by_username(new_username)
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Username already exists'}), 409
            
            user.username = new_username
        
        # Update email if provided
        if 'email' in data:
            new_email = sanitize_input(data['email'])
            is_valid, error_msg = UserValidator.validate_email(new_email)
            
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            # Check if email is already taken by another user
            existing_user = User.find_by_email(new_email)
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already exists'}), 409
            
            user.email = new_email
        
        # Update password if provided
        if 'password' in data:
            new_password = data['password']
            is_valid, error_msg = UserValidator.validate_password(new_password)
            
            if not is_valid:
                return jsonify({'error': error_msg}), 400
            
            user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Profile update failed', 'details': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if the current token is valid"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'message': 'Token is valid',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token verification failed', 'details': str(e)}), 500 