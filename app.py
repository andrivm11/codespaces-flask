from flask import Flask, render_template
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
import spacy
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datetime import datetime
from py2neo import Graph
from docx import Document




app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
faiss_index = faiss.IndexFlatL2(embedding_dim)

graph = Graph("bolt://184.72.108.88:7687", auth=("neo4j", "intents-possession-opposites"))

documents = []
metadata_store = []

documents = []
metadata_store = []

# File processing functions
def process_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = " ".join([page.extract_text() for page in reader.pages])
        metadata = {
            'title': reader.metadata.get('/Title', ''),
            'author': reader.metadata.get('/Author', ''),
            'creation_date': reader.metadata.get('/CreationDate', '')
        }
        return text, metadata

def process_docx(file_path):
    doc = Document(file_path)
    text = " ".join([paragraph.text for paragraph in doc.paragraphs])
    return text, {}

def process_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read(), {}

# Text preprocessing
def preprocess_text(text):
    doc = nlp(text)
    tokens = [
        token.lemma_.lower() 
        for token in doc 
        if not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)

# Knowledge graph functions
def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def update_knowledge_graph(text, doc_id):
    try:
        # Create document node
        graph.run(
            "MERGE (d:Document {id: $doc_id})",
            doc_id=doc_id
        )
        
        # Process entities
        entities = extract_entities(text)
        for entity, label in entities:
            graph.run(
                """
                MATCH (d:Document {id: $doc_id})
                MERGE (e:Entity {name: $name, type: $type})
                MERGE (d)-[:CONTAINS_ENTITY]->(e)
                """,
                doc_id=doc_id,
                name=entity,
                type=label
            )
    except Exception as e:
        app.logger.error(f"Knowledge graph update failed: {str(e)}")

# API endpoints
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Process document based on type
        if filename.endswith('.pdf'):
            text, metadata = process_pdf(file_path)
        elif filename.endswith('.docx'):
            text, metadata = process_docx(file_path)
        else:
            text, metadata = process_text(file_path)
        
        clean_text = preprocess_text(text)
        embedding = embedding_model.encode([clean_text])[0]
        
        doc_id = len(documents)
        documents.append({
            'id': doc_id,
            'filename': filename,
            'text': clean_text,
            'embedding': embedding.tolist(),
            'timestamp': datetime.now().isoformat()
        })
        metadata_store.append(metadata)
        
        # Update FAISS and knowledge graph
        faiss_index.add(np.array([embedding]))
        update_knowledge_graph(text, doc_id)
        
        return jsonify({
            'message': 'File processed',
            'doc_id': doc_id,
            'metadata': metadata
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def semantic_search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    
    try:
        query = data['query']
        top_k = data.get('top_k', 5)
        #print("top")
        #print(top_k)
        # Process query
        clean_query = preprocess_text(query)
        #print(clean_query)
        query_embedding = embedding_model.encode([clean_query])
        #print("querye")
        #print(query_embedding)
        #print("tipo")
        #print(type(query_embedding))
        # Search FAISS
        distances, indices = faiss_index.search(query_embedding, top_k)
        #print(distances)
        #print("indices")
        #print(indices)

        #index = faiss.IndexFlatL2(128)  # Example: an L2 index with 128 dimensions
        # ... code to add vectors to the index ...

        num_vectors = faiss_index.ntotal

        #print(f"Number of indexed vectors: {num_vectors}")
        # Format results
        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(documents):
                doc = documents[idx]
                results.append({
                    'doc_id': doc['id'],
                    'filename': doc['filename'],
                    'score': float(distances[0][idx]),
                    'excerpt': doc['text'][:200] + '...'
                })
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/entities/<int:doc_id>', methods=['GET'])
def get_entities(doc_id):
    if doc_id < 0 or doc_id >= len(documents):
        return jsonify({'error': 'Invalid document ID'}), 400
    
    try:
        entities = graph.run(
            """
            MATCH (d:Document {id: $doc_id})-[:CONTAINS_ENTITY]->(e:Entity)
            RETURN e.name AS name, e.type AS type
            """,
            doc_id=doc_id
        ).data()
        
        return jsonify({'entities': entities})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")
