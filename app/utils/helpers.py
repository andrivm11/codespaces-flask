from app.services.vector_store import documents

def validate_doc_id(doc_id):
    return 0 <= doc_id < len(documents)