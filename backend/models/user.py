from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

class User(db.Model):
    """User model for authentication and user management"""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.String(255), primary_key=True)
    
    # User information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, user_id=None):
        """Initialize user with hashed password"""
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.id = user_id or self._generate_user_id()
    
    def _generate_user_id(self):
        """Generate a unique user ID"""
        import uuid
        return str(uuid.uuid4())
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified
        }
    
    def to_dict_with_sessions(self):
        """Convert user to dictionary including session count"""
        user_dict = self.to_dict()
        user_dict['session_count'] = self.chat_sessions.count()
        return user_dict
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return User.query.get(user_id)
    
    def __repr__(self):
        return f'<User {self.username}>' 