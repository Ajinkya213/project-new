import os
import uuid
from datetime import datetime
from config.firebase_config import firebase_config
from flask import current_app
import tempfile

class FirebaseStorageService:
    """Firebase Storage Service for file uploads"""
    
    def __init__(self):
        self.bucket = firebase_config.get_storage()
        self.db = firebase_config.get_firestore()
    
    def upload_file(self, file, user_id, folder="uploads"):
        """Upload file to Firebase Storage"""
        try:
            if not file:
                return None
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create storage path
            storage_path = f"{folder}/{user_id}/{unique_filename}"
            
            # Upload to Firebase Storage
            blob = self.bucket.blob(storage_path)
            blob.upload_from_file(file.stream, content_type=file.content_type)
            
            # Make blob publicly readable (optional)
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            # Create document in Firestore
            document_data = {
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_path': storage_path,
                'file_size': file.content_length or 0,
                'file_type': file.content_type,
                'user_id': user_id,
                'public_url': public_url,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            
            # Save to Firestore
            doc_ref = self.db.collection('documents').document()
            doc_ref.set(document_data)
            document_data['id'] = doc_ref.id
            
            return document_data
            
        except Exception as e:
            print(f"Upload file error: {str(e)}")
            return None
    
    def get_user_documents(self, user_id):
        """Get all documents for a user"""
        try:
            documents = []
            query = self.db.collection('documents').where('user_id', '==', user_id).where('is_active', '==', True).order_by('created_at', direction='DESCENDING')
            
            for doc in query.stream():
                document_data = doc.to_dict()
                document_data['id'] = doc.id
                documents.append(document_data)
            
            return documents
        except Exception as e:
            print(f"Get user documents error: {str(e)}")
            return []
    
    def get_document(self, document_id, user_id=None):
        """Get a specific document"""
        try:
            doc_ref = self.db.collection('documents').document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            document_data = doc.to_dict()
            document_data['id'] = doc.id
            
            # Check if user has access to this document
            if user_id and document_data.get('user_id') != user_id:
                return None
            
            return document_data
        except Exception as e:
            print(f"Get document error: {str(e)}")
            return None
    
    def delete_document(self, document_id, user_id):
        """Delete a document"""
        try:
            # Get document to verify ownership
            document = self.get_document(document_id, user_id)
            if not document:
                return False
            
            # Delete from Firebase Storage
            blob = self.bucket.blob(document['file_path'])
            if blob.exists():
                blob.delete()
            
            # Soft delete from Firestore
            self.db.collection('documents').document(document_id).update({
                'is_active': False,
                'updated_at': datetime.utcnow()
            })
            
            return True
        except Exception as e:
            print(f"Delete document error: {str(e)}")
            return False
    
    def get_download_url(self, document_id, user_id=None):
        """Get download URL for a document"""
        try:
            document = self.get_document(document_id, user_id)
            if not document:
                return None
            
            # Generate signed URL for private files
            blob = self.bucket.blob(document['file_path'])
            if blob.exists():
                # Generate signed URL that expires in 1 hour
                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(hours=1),
                    method="GET"
                )
                return signed_url
            
            return document.get('public_url')
        except Exception as e:
            print(f"Get download URL error: {str(e)}")
            return None
    
    def upload_file_from_path(self, file_path, user_id, original_filename=None, folder="uploads"):
        """Upload file from local path"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Generate unique filename
            file_extension = os.path.splitext(file_path)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create storage path
            storage_path = f"{folder}/{user_id}/{unique_filename}"
            
            # Upload to Firebase Storage
            blob = self.bucket.blob(storage_path)
            
            with open(file_path, 'rb') as file:
                blob.upload_from_file(file)
            
            # Make blob publicly readable (optional)
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Get content type
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create document in Firestore
            document_data = {
                'filename': unique_filename,
                'original_filename': original_filename or os.path.basename(file_path),
                'file_path': storage_path,
                'file_size': file_size,
                'file_type': content_type,
                'user_id': user_id,
                'public_url': public_url,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            
            # Save to Firestore
            doc_ref = self.db.collection('documents').document()
            doc_ref.set(document_data)
            document_data['id'] = doc_ref.id
            
            return document_data
            
        except Exception as e:
            print(f"Upload file from path error: {str(e)}")
            return None

# Global storage service instance
firebase_storage_service = FirebaseStorageService() 