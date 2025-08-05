from flask import jsonify, request
from functools import wraps
from config.firebase_config import firebase_config
import firebase_admin
from firebase_admin import auth
import uuid
from datetime import datetime

class FirebaseAuthService:
    """Firebase Authentication Service"""
    
    def __init__(self):
        self.auth = firebase_config.get_auth()
        self.db = firebase_config.get_firestore()
    
    def verify_token(self, id_token):
        """Verify Firebase ID token and return user info"""
        try:
            decoded_token = firebase_config.verify_id_token(id_token)
            if decoded_token:
                return {
                    'uid': decoded_token['uid'],
                    'email': decoded_token.get('email'),
                    'name': decoded_token.get('name', ''),
                    'email_verified': decoded_token.get('email_verified', False)
                }
            return None
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            return None
    
    def create_user(self, email, password, name=None):
        """Create new user in Firebase Auth"""
        try:
            user_properties = {
                'email': email,
                'password': password,
                'email_verified': False
            }
            
            if name:
                user_properties['display_name'] = name
            
            user = self.auth.create_user(**user_properties)
            
            # Create user document in Firestore
            user_data = {
                'uid': user.uid,
                'email': user.email,
                'name': name or '',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'email_verified': user.email_verified
            }
            
            self.db.collection('users').document(user.uid).set(user_data)
            
            return {
                'uid': user.uid,
                'email': user.email,
                'name': name or '',
                'email_verified': user.email_verified
            }
        except Exception as e:
            print(f"User creation error: {str(e)}")
            return None
    
    def get_user(self, uid):
        """Get user by UID"""
        try:
            user = self.auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'name': user.display_name or '',
                'email_verified': user.email_verified
            }
        except Exception as e:
            print(f"Get user error: {str(e)}")
            return None
    
    def update_user(self, uid, **kwargs):
        """Update user profile"""
        try:
            user = self.auth.update_user(uid, **kwargs)
            
            # Update user document in Firestore
            user_data = {
                'updated_at': datetime.utcnow()
            }
            
            if 'display_name' in kwargs:
                user_data['name'] = kwargs['display_name']
            
            self.db.collection('users').document(uid).update(user_data)
            
            return {
                'uid': user.uid,
                'email': user.email,
                'name': user.display_name or '',
                'email_verified': user.email_verified
            }
        except Exception as e:
            print(f"Update user error: {str(e)}")
            return None
    
    def delete_user(self, uid):
        """Delete user"""
        try:
            self.auth.delete_user(uid)
            
            # Delete user document from Firestore
            self.db.collection('users').document(uid).delete()
            
            return True
        except Exception as e:
            print(f"Delete user error: {str(e)}")
            return False

# Global auth service instance
firebase_auth_service = FirebaseAuthService()

def require_auth(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'error': 'Authorization header with Bearer token is required'
                }), 401
            
            # Extract token
            id_token = auth_header.split('Bearer ')[1]
            
            # Verify token with Firebase
            user_info = firebase_auth_service.verify_token(id_token)
            if not user_info:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token'
                }), 401
            
            # Add user info to request
            request.user = user_info
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed'
            }), 401
    
    return decorated_function 