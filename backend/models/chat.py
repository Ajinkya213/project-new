from datetime import datetime
from .database import db

class ChatSession(db.Model):
    """Chat session model"""
    
    __tablename__ = 'chat_sessions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Session information
    title = db.Column(db.String(255), nullable=False)
    
    # Foreign key to user
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Session status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('Message', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, user_id):
        """Initialize chat session"""
        self.title = title
        self.user_id = user_id
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'message_count': self.messages.count()
        }
    
    def to_dict_with_messages(self):
        """Convert session to dictionary including messages"""
        session_dict = self.to_dict()
        session_dict['messages'] = [message.to_dict() for message in self.messages.order_by(Message.created_at.asc()).all()]
        return session_dict
    
    def update_title(self, new_title):
        """Update session title"""
        self.title = new_title
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate session"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<ChatSession {self.id}: {self.title}>'


class Message(db.Model):
    """Message model for chat messages"""
    
    __tablename__ = 'messages'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Message content
    text = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    
    # Foreign key to chat session
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Message status
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __init__(self, text, sender, session_id):
        """Initialize message"""
        self.text = text
        self.sender = sender
        self.session_id = session_id
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'sender': self.sender,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
    
    def update_text(self, new_text):
        """Update message text"""
        self.text = new_text
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete message"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Message {self.id}: {self.text[:50]}...>'


class Document(db.Model):
    """Document model for file uploads"""
    
    __tablename__ = 'documents'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_type = db.Column(db.String(100), nullable=False)
    
    # Foreign key to user
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Document status
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, filename, original_filename, file_path, file_size, file_type, user_id):
        """Initialize document"""
        self.filename = filename
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        self.user_id = user_id
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def deactivate(self):
        """Deactivate document"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Document {self.id}: {self.original_filename}>' 