from flask import Blueprint, request, jsonify
from services.api_key_service import api_key_service
from services.firebase_auth_service import require_auth
from datetime import datetime

api_keys_bp = Blueprint('api_keys', __name__)

@api_keys_bp.route('/keys', methods=['GET'])
@require_auth
def get_user_api_keys():
    """Get user's API keys"""
    try:
        user_info = request.user
        keys = api_key_service.get_user_api_keys(user_info['uid'])
        
        return jsonify({
            'success': True,
            'keys': keys
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get API keys: {str(e)}'
        }), 500

@api_keys_bp.route('/keys/status', methods=['GET'])
@require_auth
def get_user_key_status():
    """Get status of user's API keys"""
    try:
        user_info = request.user
        status = api_key_service.get_user_key_status(user_info['uid'])
        
        return jsonify({
            'success': True,
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get key status: {str(e)}'
        }), 500

@api_keys_bp.route('/keys/available', methods=['GET'])
@require_auth
def get_available_api_keys():
    """Get information about available API keys"""
    try:
        available_keys = api_key_service.get_available_api_keys()
        
        return jsonify({
            'success': True,
            'available_keys': available_keys
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get available keys: {str(e)}'
        }), 500

@api_keys_bp.route('/keys', methods=['POST'])
@require_auth
def store_api_key():
    """Store user's API key"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        key_name = data.get('key_name', '').strip()
        api_key = data.get('api_key', '').strip()
        validate_key = data.get('validate', True)  # Default to true
        
        if not key_name or not api_key:
            return jsonify({
                'success': False,
                'error': 'Key name and API key are required'
            }), 400
        
        # Validate key name
        available_keys = api_key_service.get_available_api_keys()
        if key_name not in available_keys:
            return jsonify({
                'success': False,
                'error': f'Invalid key name: {key_name}'
            }), 400
        
        # Validate API key if requested
        if validate_key:
            is_valid = api_key_service.validate_api_key(key_name, api_key)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'Invalid API key for {key_name}'
                }), 400
        
        # Store the API key
        success = api_key_service.store_user_api_key(user_info['uid'], key_name, api_key)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'API key {key_name} stored successfully',
                'key_name': key_name,
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to store API key {key_name}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to store API key: {str(e)}'
        }), 500

@api_keys_bp.route('/keys/<key_name>', methods=['DELETE'])
@require_auth
def delete_api_key(key_name):
    """Delete user's API key"""
    try:
        user_info = request.user
        
        # Validate key name
        available_keys = api_key_service.get_available_api_keys()
        if key_name not in available_keys:
            return jsonify({
                'success': False,
                'error': f'Invalid key name: {key_name}'
            }), 400
        
        success = api_key_service.delete_user_api_key(user_info['uid'], key_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'API key {key_name} deleted successfully',
                'key_name': key_name,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to delete API key {key_name}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete API key: {str(e)}'
        }), 500

@api_keys_bp.route('/keys/<key_name>/validate', methods=['POST'])
@require_auth
def validate_api_key(key_name):
    """Validate user's API key"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        # Validate key name
        available_keys = api_key_service.get_available_api_keys()
        if key_name not in available_keys:
            return jsonify({
                'success': False,
                'error': f'Invalid key name: {key_name}'
            }), 400
        
        # Validate the API key
        is_valid = api_key_service.validate_api_key(key_name, api_key)
        
        return jsonify({
            'success': True,
            'key_name': key_name,
            'is_valid': is_valid,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to validate API key: {str(e)}'
        }), 500

@api_keys_bp.route('/keys/test', methods=['POST'])
@require_auth
def test_api_key():
    """Test API key without storing it"""
    try:
        user_info = request.user
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        key_name = data.get('key_name', '').strip()
        api_key = data.get('api_key', '').strip()
        
        if not key_name or not api_key:
            return jsonify({
                'success': False,
                'error': 'Key name and API key are required'
            }), 400
        
        # Validate key name
        available_keys = api_key_service.get_available_api_keys()
        if key_name not in available_keys:
            return jsonify({
                'success': False,
                'error': f'Invalid key name: {key_name}'
            }), 400
        
        # Test the API key
        is_valid = api_key_service.validate_api_key(key_name, api_key)
        
        return jsonify({
            'success': True,
            'key_name': key_name,
            'is_valid': is_valid,
            'key_info': available_keys.get(key_name, {}),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to test API key: {str(e)}'
        }), 500 