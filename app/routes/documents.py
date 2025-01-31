from flask import Blueprint, request, jsonify
from app.services.file_processing import process_uploaded_file
from app.services.vector_store import search_documents
from app.services.knowledge_graph import get_document_entities
from app.utils.helpers import validate_doc_id

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    try:
        result = process_uploaded_file(request.files['file'])
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/search', methods=['POST'])
def semantic_search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    try:
        results = search_documents(data['query'], data.get('top_k', 5))
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/entities/<int:doc_id>', methods=['GET'])
def get_entities(doc_id):
    if not validate_doc_id(doc_id):
        return jsonify({'error': 'Invalid document ID'}), 400
    
    try:
        entities = get_document_entities(doc_id)
        return jsonify({'entities': entities})
    except Exception as e:
        return jsonify({'error': str(e)}), 500