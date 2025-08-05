from flask import Blueprint, request, jsonify, send_from_directory
from services.local_storage_service import local_storage_service
from services.firebase_auth_service import require_auth
import os

bp = Blueprint('api', __name__)

@bp.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload file to local storage"""
    try:
        user_info = request.user
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Upload file to local storage
        document_data = local_storage_service.upload_file(file, user_info['uid'])
        
        if not document_data:
            return jsonify({
                'success': False,
                'error': 'Failed to upload file'
            }), 500
        
        return jsonify({
            'success': True,
            'document': document_data
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@bp.route('/documents', methods=['GET'])
@require_auth
def get_documents():
    """Get all documents for the authenticated user"""
    try:
        user_info = request.user
        documents = local_storage_service.get_user_documents(user_info['uid'])
        
        return jsonify({
            'success': True,
            'documents': documents
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get documents: {str(e)}'
        }), 500

@bp.route('/documents/<document_id>', methods=['GET'])
@require_auth
def get_document(document_id):
    """Get a specific document"""
    try:
        user_info = request.user
        document = local_storage_service.get_document(document_id, user_info['uid'])
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': document
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get document: {str(e)}'
        }), 500

@bp.route('/documents/<document_id>/download', methods=['GET'])
@require_auth
def download_document(document_id):
    """Download a document"""
    try:
        user_info = request.user
        document = local_storage_service.get_document(document_id, user_info['uid'])
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found or access denied'
            }), 404
        
        # Serve file from local storage
        user_folder = local_storage_service.get_user_folder(user_info['uid'])
        return send_from_directory(
            user_folder, 
            document_id, 
            as_attachment=True,
            download_name=document.get('original_filename', document_id)
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to download document: {str(e)}'
        }), 500

@bp.route('/documents/<document_id>', methods=['DELETE'])
@require_auth
def delete_document(document_id):
    """Delete a document"""
    try:
        user_info = request.user
        success = local_storage_service.delete_document(document_id, user_info['uid'])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete document'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete document: {str(e)}'
        }), 500

@bp.route('/uploads/<user_id>/<filename>', methods=['GET'])
def serve_file(user_id, filename):
    """Serve uploaded files (for direct access)"""
    try:
        # Basic security check - in production, you'd want more robust validation
        user_folder = os.path.join(local_storage_service.upload_folder, str(user_id))
        file_path = os.path.join(user_folder, filename)
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_from_directory(user_folder, filename)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to serve file: {str(e)}'
        }), 500 