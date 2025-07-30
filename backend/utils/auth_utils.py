from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from functools import wraps
from flask import jsonify, request
from models.user import User

def generate_tokens(user_id):
    """Generate access and refresh tokens for a user"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

def get_current_user():
    """Get current user from JWT token"""
    user_id = get_jwt_identity()
    if user_id:
        return User.find_by_id(user_id)
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_ownership(model_class, id_param='id'):
    """Decorator to require ownership of a resource"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            resource_id = kwargs.get(id_param)
            
            if not resource_id:
                return jsonify({'error': f'{id_param} parameter required'}), 400
            
            # Get the resource
            resource = model_class.query.get(resource_id)
            if not resource:
                return jsonify({'error': 'Resource not found'}), 404
            
            # Check ownership
            if hasattr(resource, 'user_id') and resource.user_id != user.id:
                return jsonify({'error': 'Access denied'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_user_input(data, required_fields):
    """Validate user input data"""
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    return errors

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    import re
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)
    
    return text.strip()

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid" 