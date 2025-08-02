from flask import Blueprint, request, jsonify
from werkzeug.datastructures import FileStorage
from services.query_service import process_query, process_documents

bp = Blueprint('api', __name__)

@bp.route("/upload/", methods=['POST'])
async def upload():
    files = request.files.getlist('files')
    return await process_documents(files)

@bp.route("/query/", methods=['POST'])
async def query():
    data = request.get_json()
    query_text = data.get('query', '')
    return await process_query(query_text)