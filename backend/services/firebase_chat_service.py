from datetime import datetime
from config.firebase_config import firebase_config
from flask import jsonify
import uuid

class FirebaseChatService:
    """Firebase Chat Service using Firestore"""
    
    def __init__(self):
        self.db = firebase_config.get_firestore()
    
    def create_chat_session(self, user_id, title="New Chat"):
        """Create a new chat session"""
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                'id': session_id,
                'title': title,
                'user_id': user_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True,
                'message_count': 0
            }
            
            # Create session document
            self.db.collection('chat_sessions').document(session_id).set(session_data)
            
            return session_data
        except Exception as e:
            print(f"Create chat session error: {str(e)}")
            return None
    
    def get_chat_sessions(self, user_id):
        """Get all chat sessions for a user"""
        try:
            sessions = []
            query = self.db.collection('chat_sessions').where('user_id', '==', user_id).where('is_active', '==', True).order_by('updated_at', direction='DESCENDING')
            
            for doc in query.stream():
                session_data = doc.to_dict()
                session_data['id'] = doc.id
                sessions.append(session_data)
            
            return sessions
        except Exception as e:
            print(f"Get chat sessions error: {str(e)}")
            return []
    
    def get_chat_session(self, session_id, user_id=None):
        """Get a specific chat session with messages"""
        try:
            doc_ref = self.db.collection('chat_sessions').document(session_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            session_data = doc.to_dict()
            session_data['id'] = doc.id
            
            # Check if user has access to this session
            if user_id and session_data.get('user_id') != user_id:
                return None
            
            # Get messages for this session
            messages = self.get_messages(session_id)
            session_data['messages'] = messages
            
            return session_data
        except Exception as e:
            print(f"Get chat session error: {str(e)}")
            return None
    
    def update_chat_session(self, session_id, **kwargs):
        """Update chat session"""
        try:
            update_data = {
                'updated_at': datetime.utcnow()
            }
            update_data.update(kwargs)
            
            self.db.collection('chat_sessions').document(session_id).update(update_data)
            return True
        except Exception as e:
            print(f"Update chat session error: {str(e)}")
            return False
    
    def delete_chat_session(self, session_id, user_id):
        """Soft delete chat session"""
        try:
            # Verify ownership
            session = self.get_chat_session(session_id, user_id)
            if not session:
                return False
            
            # Soft delete
            self.db.collection('chat_sessions').document(session_id).update({
                'is_active': False,
                'updated_at': datetime.utcnow()
            })
            
            return True
        except Exception as e:
            print(f"Delete chat session error: {str(e)}")
            return False
    
    def add_message(self, session_id, text, sender, user_id):
        """Add a message to a chat session"""
        try:
            # Verify session exists and user has access
            session = self.get_chat_session(session_id, user_id)
            if not session:
                return None
            
            message_id = str(uuid.uuid4())
            message_data = {
                'id': message_id,
                'text': text,
                'sender': sender,  # 'user' or 'ai'
                'session_id': session_id,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_deleted': False
            }
            
            # Add message to Firestore
            self.db.collection('messages').document(message_id).set(message_data)
            
            # Update session message count and timestamp
            self.db.collection('chat_sessions').document(session_id).update({
                'message_count': session.get('message_count', 0) + 1,
                'updated_at': datetime.utcnow()
            })
            
            return message_data
        except Exception as e:
            print(f"Add message error: {str(e)}")
            return None
    
    def get_messages(self, session_id):
        """Get all messages for a session"""
        try:
            messages = []
            query = self.db.collection('messages').where('session_id', '==', session_id).where('is_deleted', '==', False).order_by('created_at')
            
            for doc in query.stream():
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                messages.append(message_data)
            
            return messages
        except Exception as e:
            print(f"Get messages error: {str(e)}")
            return []
    
    def update_message(self, message_id, text, user_id):
        """Update a message"""
        try:
            # Get message to verify ownership
            doc_ref = self.db.collection('messages').document(message_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            message_data = doc.to_dict()
            
            # Check if message belongs to user (for user messages only)
            if message_data.get('sender') == 'user':
                session = self.get_chat_session(message_data.get('session_id'), user_id)
                if not session:
                    return False
            
            # Update message
            doc_ref.update({
                'text': text,
                'updated_at': datetime.utcnow()
            })
            
            return True
        except Exception as e:
            print(f"Update message error: {str(e)}")
            return False
    
    def delete_message(self, message_id, user_id):
        """Soft delete a message"""
        try:
            # Get message to verify ownership
            doc_ref = self.db.collection('messages').document(message_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            message_data = doc.to_dict()
            
            # Check if message belongs to user (for user messages only)
            if message_data.get('sender') == 'user':
                session = self.get_chat_session(message_data.get('session_id'), user_id)
                if not session:
                    return False
            
            # Soft delete
            doc_ref.update({
                'is_deleted': True,
                'updated_at': datetime.utcnow()
            })
            
            return True
        except Exception as e:
            print(f"Delete message error: {str(e)}")
            return False

# Global chat service instance
firebase_chat_service = FirebaseChatService() 