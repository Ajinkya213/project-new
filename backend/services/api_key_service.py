import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from services.firebase_auth_service import require_auth
from services.firebase_chat_service import firebase_chat_service
from core.rag_singleton import get_rag

class APIKeyService:
    """Secure API key management service with Firebase integration"""
    
    def __init__(self):
        self.rag = get_rag()
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Default API keys from environment (for fallback)
        self.default_keys = {
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
            'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY'),
            'QDRANT_API_KEY': os.getenv('QDRANT_API_KEY'),
            'QDRANT_URL': os.getenv('QDRANT_URL', 'http://localhost:6333')
        }
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API keys"""
        key_file = 'encryption_key.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key"""
        if not api_key:
            return ""
        encrypted = self.cipher_suite.encrypt(api_key.encode())
        return encrypted.decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        if not encrypted_key:
            return ""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Failed to decrypt API key: {str(e)}")
            return ""
    
    def store_user_api_key(self, user_id: str, key_name: str, api_key: str) -> bool:
        """Store user's API key securely"""
        try:
            # Encrypt the API key
            encrypted_key = self._encrypt_api_key(api_key)
            
            # Store in Firestore
            key_data = {
                'user_id': user_id,
                'key_name': key_name,
                'encrypted_key': encrypted_key,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            
            # Check if key already exists
            existing_key = self.get_user_api_key(user_id, key_name)
            if existing_key:
                # Update existing key
                self.rag.db.collection('user_api_keys')\
                    .where('user_id', '==', user_id)\
                    .where('key_name', '==', key_name)\
                    .limit(1)\
                    .stream()
                
                # Update the document
                for doc in self.rag.db.collection('user_api_keys')\
                    .where('user_id', '==', user_id)\
                    .where('key_name', '==', key_name)\
                    .stream():
                    doc.reference.update({
                        'encrypted_key': encrypted_key,
                        'updated_at': datetime.utcnow()
                    })
                    return True
            else:
                # Create new key
                self.rag.db.collection('user_api_keys').add(key_data)
                return True
                
        except Exception as e:
            print(f"Failed to store API key: {str(e)}")
            return False
    
    def get_user_api_key(self, user_id: str, key_name: str) -> Optional[str]:
        """Get user's API key"""
        try:
            # Query Firestore for the key
            docs = self.rag.db.collection('user_api_keys')\
                .where('user_id', '==', user_id)\
                .where('key_name', '==', key_name)\
                .where('is_active', '==', True)\
                .limit(1)\
                .stream()
            
            for doc in docs:
                data = doc.to_dict()
                encrypted_key = data.get('encrypted_key', '')
                return self._decrypt_api_key(encrypted_key)
            
            return None
            
        except Exception as e:
            print(f"Failed to get API key: {str(e)}")
            return None
    
    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            keys = []
            docs = self.rag.db.collection('user_api_keys')\
                .where('user_id', '==', user_id)\
                .where('is_active', '==', True)\
                .stream()
            
            for doc in docs:
                data = doc.to_dict()
                keys.append({
                    'id': doc.id,
                    'key_name': data.get('key_name'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'is_active': data.get('is_active', True)
                })
            
            return keys
            
        except Exception as e:
            print(f"Failed to get user API keys: {str(e)}")
            return []
    
    def delete_user_api_key(self, user_id: str, key_name: str) -> bool:
        """Delete user's API key"""
        try:
            # Soft delete by setting is_active to False
            docs = self.rag.db.collection('user_api_keys')\
                .where('user_id', '==', user_id)\
                .where('key_name', '==', key_name)\
                .stream()
            
            for doc in docs:
                doc.reference.update({
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                })
                return True
            
            return False
            
        except Exception as e:
            print(f"Failed to delete API key: {str(e)}")
            return False
    
    def get_api_key_for_agent(self, user_id: str, agent_type: str) -> Dict[str, str]:
        """Get API keys needed for a specific agent"""
        keys = {}
        
        # Map agent types to required API keys
        agent_key_requirements = {
            'multimodal': ['GEMINI_API_KEY', 'TAVILY_API_KEY'],
            'document': ['GEMINI_API_KEY'],
            'research': ['TAVILY_API_KEY'],
            'lightweight': ['GEMINI_API_KEY'],
            'chat': ['GEMINI_API_KEY']
        }
        
        required_keys = agent_key_requirements.get(agent_type, ['GEMINI_API_KEY'])
        
        for key_name in required_keys:
            # Try user's key first
            user_key = self.get_user_api_key(user_id, key_name)
            if user_key:
                keys[key_name] = user_key
            else:
                # Fallback to default key
                default_key = self.default_keys.get(key_name)
                if default_key:
                    keys[key_name] = default_key
        
        return keys
    
    def validate_api_key(self, key_name: str, api_key: str) -> bool:
        """Validate API key by making a test request"""
        try:
            if key_name == 'GEMINI_API_KEY':
                return self._validate_gemini_key(api_key)
            elif key_name == 'TAVILY_API_KEY':
                return self._validate_tavily_key(api_key)
            elif key_name == 'QDRANT_API_KEY':
                return self._validate_qdrant_key(api_key)
            else:
                return True  # Unknown key type, assume valid
        except Exception as e:
            print(f"API key validation failed: {str(e)}")
            return False
    
    def _validate_gemini_key(self, api_key: str) -> bool:
        """Validate Gemini API key"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Hello")
            return response is not None
        except Exception as e:
            print(f"Gemini key validation failed: {str(e)}")
            return False
    
    def _validate_tavily_key(self, api_key: str) -> bool:
        """Validate Tavily API key"""
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            response = client.search("test")
            return response is not None
        except Exception as e:
            print(f"Tavily key validation failed: {str(e)}")
            return False
    
    def _validate_qdrant_key(self, api_key: str) -> bool:
        """Validate Qdrant API key"""
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=self.default_keys.get('QDRANT_URL', 'http://localhost:6333'), api_key=api_key)
            collections = client.get_collections()
            return collections is not None
        except Exception as e:
            print(f"Qdrant key validation failed: {str(e)}")
            return False
    
    def get_available_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available API keys"""
        return {
            'GEMINI_API_KEY': {
                'name': 'Google Gemini API',
                'description': 'Required for AI text generation and document analysis',
                'url': 'https://makersuite.google.com/app/apikey',
                'required_for': ['multimodal', 'document', 'lightweight', 'chat']
            },
            'TAVILY_API_KEY': {
                'name': 'Tavily Search API',
                'description': 'Required for web search and research',
                'url': 'https://tavily.com/',
                'required_for': ['multimodal', 'research']
            },
            'QDRANT_API_KEY': {
                'name': 'Qdrant Vector Database API',
                'description': 'Required for vector search and document retrieval',
                'url': 'https://qdrant.tech/',
                'required_for': ['multimodal', 'document']
            }
        }
    
    def get_user_key_status(self, user_id: str) -> Dict[str, Any]:
        """Get status of user's API keys"""
        try:
            user_keys = self.get_user_api_keys(user_id)
            available_keys = self.get_available_api_keys()
            
            status = {}
            for key_name, key_info in available_keys.items():
                user_has_key = any(k['key_name'] == key_name for k in user_keys)
                status[key_name] = {
                    'name': key_info['name'],
                    'description': key_info['description'],
                    'url': key_info['url'],
                    'required_for': key_info['required_for'],
                    'user_has_key': user_has_key,
                    'is_valid': user_has_key  # Could add validation here
                }
            
            return status
            
        except Exception as e:
            print(f"Failed to get user key status: {str(e)}")
            return {}

# Global API key service instance
api_key_service = APIKeyService() 