import os
import uuid
import shutil
from datetime import datetime
from flask import current_app
import mimetypes
from werkzeug.utils import secure_filename

class LocalStorageService:
    """Local Storage Service for file uploads"""
    
    def __init__(self):
        self.upload_folder = os.path.join(os.getcwd(), 'uploads')
        self.ensure_upload_folder()
    
    def ensure_upload_folder(self):
        """Ensure upload folder exists"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def get_user_folder(self, user_id):
        """Get user-specific folder path"""
        user_folder = os.path.join(self.upload_folder, str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        return user_folder
    
    def upload_file(self, file, user_id, folder="uploads"):
        """Upload file to local storage"""
        try:
            if not file:
                return None
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create user-specific folder
            user_folder = self.get_user_folder(user_id)
            
            # Create storage path
            storage_path = os.path.join(user_folder, unique_filename)
            
            # Save file to local storage
            file.save(storage_path)
            
            # Get file size
            file_size = os.path.getsize(storage_path)
            
            # Get content type
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
            
            # Create document data
            document_data = {
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_path': storage_path,
                'file_size': file_size,
                'file_type': content_type,
                'user_id': user_id,
                'local_url': f'/uploads/{user_id}/{unique_filename}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            
            return document_data
            
        except Exception as e:
            print(f"Upload file error: {str(e)}")
            return None
    
    def get_user_documents(self, user_id):
        """Get all documents for a user from local storage"""
        try:
            user_folder = self.get_user_folder(user_id)
            documents = []
            
            if os.path.exists(user_folder):
                for filename in os.listdir(user_folder):
                    file_path = os.path.join(user_folder, filename)
                    if os.path.isfile(file_path):
                        # Get file stats
                        stat = os.stat(file_path)
                        
                        # Try to get original filename from metadata or use current filename
                        original_filename = filename
                        
                        # Get content type
                        content_type, _ = mimetypes.guess_type(file_path)
                        if not content_type:
                            content_type = 'application/octet-stream'
                        
                        document_data = {
                            'filename': filename,
                            'original_filename': original_filename,
                            'file_path': file_path,
                            'file_size': stat.st_size,
                            'file_type': content_type,
                            'user_id': user_id,
                            'local_url': f'/uploads/{user_id}/{filename}',
                            'created_at': datetime.fromtimestamp(stat.st_ctime),
                            'updated_at': datetime.fromtimestamp(stat.st_mtime),
                            'is_active': True
                        }
                        documents.append(document_data)
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x['created_at'], reverse=True)
            return documents
            
        except Exception as e:
            print(f"Get user documents error: {str(e)}")
            return []
    
    def get_document(self, document_id, user_id):
        """Get a specific document by ID (filename)"""
        try:
            user_folder = self.get_user_folder(user_id)
            file_path = os.path.join(user_folder, document_id)
            
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return None
            
            # Get file stats
            stat = os.stat(file_path)
            
            # Get content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            document_data = {
                'filename': document_id,
                'original_filename': document_id,  # We don't store original names in local storage
                'file_path': file_path,
                'file_size': stat.st_size,
                'file_type': content_type,
                'user_id': user_id,
                'local_url': f'/uploads/{user_id}/{document_id}',
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'updated_at': datetime.fromtimestamp(stat.st_mtime),
                'is_active': True
            }
            
            return document_data
            
        except Exception as e:
            print(f"Get document error: {str(e)}")
            return None
    
    def delete_document(self, document_id, user_id):
        """Delete a document from local storage"""
        try:
            user_folder = self.get_user_folder(user_id)
            file_path = os.path.join(user_folder, document_id)
            
            if not os.path.exists(file_path):
                return False
            
            # Delete file
            os.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"Delete document error: {str(e)}")
            return False
    
    def get_download_url(self, document_id, user_id):
        """Get download URL for a document"""
        try:
            user_folder = self.get_user_folder(user_id)
            file_path = os.path.join(user_folder, document_id)
            
            if not os.path.exists(file_path):
                return None
            
            # Return local URL for download
            return f'/uploads/{user_id}/{document_id}'
            
        except Exception as e:
            print(f"Get download URL error: {str(e)}")
            return None
    
    def upload_file_from_path(self, file_path, user_id, original_filename=None):
        """Upload file from local path"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Generate unique filename
            file_extension = os.path.splitext(file_path)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create user-specific folder
            user_folder = self.get_user_folder(user_id)
            
            # Create storage path
            storage_path = os.path.join(user_folder, unique_filename)
            
            # Copy file to storage
            shutil.copy2(file_path, storage_path)
            
            # Get file size
            file_size = os.path.getsize(storage_path)
            
            # Get content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create document data
            document_data = {
                'filename': unique_filename,
                'original_filename': original_filename or os.path.basename(file_path),
                'file_path': storage_path,
                'file_size': file_size,
                'file_type': content_type,
                'user_id': user_id,
                'local_url': f'/uploads/{user_id}/{unique_filename}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            
            return document_data
            
        except Exception as e:
            print(f"Upload file from path error: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_old=30):
        """Clean up old files (optional maintenance)"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            for user_folder in os.listdir(self.upload_folder):
                user_path = os.path.join(self.upload_folder, user_folder)
                if os.path.isdir(user_path):
                    for filename in os.listdir(user_path):
                        file_path = os.path.join(user_path, filename)
                        if os.path.isfile(file_path):
                            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            if file_time < cutoff_date:
                                os.remove(file_path)
                                print(f"Cleaned up old file: {file_path}")
                                
        except Exception as e:
            print(f"Cleanup error: {str(e)}")

# Global storage service instance
local_storage_service = LocalStorageService() 