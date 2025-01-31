import os
import PyPDF2
from docx import Document
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app.services.vector_store import add_document_embedding
from app.services.knowledge_graph import update_knowledge_graph
from app.services.text_processing import preprocess_text

def process_uploaded_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        if filename.endswith('.pdf'):
            text, metadata = process_pdf(file_path)
        elif filename.endswith('.docx'):
            text, metadata = process_docx(file_path)
        else:
            text, metadata = process_text(file_path)

        clean_text = preprocess_text(text)
        doc_id = add_document_embedding(clean_text, filename)
        update_knowledge_graph(text, doc_id)
        
        return {
            'message': 'File processed',
            'doc_id': doc_id,
            'metadata': metadata
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def process_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = " ".join(page.extract_text() for page in reader.pages)
        return text, {
            'title': reader.metadata.get('/Title', ''),
            'author': reader.metadata.get('/Author', ''),
            'creation_date': reader.metadata.get('/CreationDate', '')
        }

def process_docx(file_path):
    doc = Document(file_path)
    return " ".join(p.text for p in doc.paragraphs), {}

def process_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read(), {}