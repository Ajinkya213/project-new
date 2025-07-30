import re
from typing import List, Tuple, Optional

class MessageValidator:
    """Validator for chat messages"""
    
    MAX_MESSAGE_LENGTH = 5000
    MIN_MESSAGE_LENGTH = 1
    
    @staticmethod
    def validate_message(text: str) -> Tuple[bool, str]:
        """Validate message text"""
        if not text:
            return False, "Message cannot be empty"
        
        if len(text.strip()) < MessageValidator.MIN_MESSAGE_LENGTH:
            return False, f"Message must be at least {MessageValidator.MIN_MESSAGE_LENGTH} character long"
        
        if len(text) > MessageValidator.MAX_MESSAGE_LENGTH:
            return False, f"Message cannot exceed {MessageValidator.MAX_MESSAGE_LENGTH} characters"
        
        # Check for potentially harmful content
        if MessageValidator._contains_suspicious_content(text):
            return False, "Message contains inappropriate content"
        
        return True, "Message is valid"
    
    @staticmethod
    def _contains_suspicious_content(text: str) -> bool:
        """Check for suspicious content in message"""
        suspicious_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>',
            r'<object.*?>',
            r'<embed.*?>'
        ]
        
        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False

class SessionValidator:
    """Validator for chat sessions"""
    
    MAX_TITLE_LENGTH = 255
    MIN_TITLE_LENGTH = 1
    
    @staticmethod
    def validate_title(title: str) -> Tuple[bool, str]:
        """Validate session title"""
        if not title:
            return False, "Session title cannot be empty"
        
        if len(title.strip()) < SessionValidator.MIN_TITLE_LENGTH:
            return False, f"Title must be at least {SessionValidator.MIN_TITLE_LENGTH} character long"
        
        if len(title) > SessionValidator.MAX_TITLE_LENGTH:
            return False, f"Title cannot exceed {SessionValidator.MAX_TITLE_LENGTH} characters"
        
        return True, "Title is valid"

class UserValidator:
    """Validator for user data"""
    
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 80
    MIN_PASSWORD_LENGTH = 8
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username"""
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < UserValidator.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {UserValidator.MIN_USERNAME_LENGTH} characters long"
        
        if len(username) > UserValidator.MAX_USERNAME_LENGTH:
            return False, f"Username cannot exceed {UserValidator.MAX_USERNAME_LENGTH} characters"
        
        # Check for valid characters (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not email:
            return False, "Email cannot be empty"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, "Email is valid"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < UserValidator.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {UserValidator.MIN_PASSWORD_LENGTH} characters long"
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"

class FileValidator:
    """Validator for file uploads"""
    
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'
    }
    
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def validate_file_extension(filename: str) -> Tuple[bool, str]:
        """Validate file extension"""
        if not filename:
            return False, "Filename cannot be empty"
        
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if extension not in FileValidator.ALLOWED_EXTENSIONS:
            return False, f"File type '{extension}' is not allowed. Allowed types: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
        
        return True, "File extension is valid"
    
    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, str]:
        """Validate file size"""
        if file_size > FileValidator.MAX_FILE_SIZE:
            max_size_mb = FileValidator.MAX_FILE_SIZE // (1024 * 1024)
            return False, f"File size cannot exceed {max_size_mb}MB"
        
        return True, "File size is valid"

class PaginationValidator:
    """Validator for pagination parameters"""
    
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 20
    
    @staticmethod
    def validate_pagination_params(page: int, per_page: int) -> Tuple[bool, str, dict]:
        """Validate pagination parameters"""
        if page < 1:
            return False, "Page number must be greater than 0", {}
        
        if per_page < 1:
            return False, "Per page must be greater than 0", {}
        
        if per_page > PaginationValidator.MAX_PER_PAGE:
            return False, f"Per page cannot exceed {PaginationValidator.MAX_PER_PAGE}", {}
        
        return True, "Pagination parameters are valid", {
            'page': page,
            'per_page': per_page
        } 