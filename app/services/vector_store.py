import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
from app.services.text_processing import preprocess_text


documents = []
embedding_model = None
faiss_index = None

def initialize_faiss(app):
    global faiss_index, embedding_model
    embedding_dim = 384
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    try:
        faiss_index = faiss.read_index(app.config['FAISS_INDEX_PATH'])
    except:
        faiss_index = faiss.IndexFlatL2(embedding_dim)

def add_document_embedding(text, filename):
    embedding = embedding_model.encode([text])[0]
    faiss_index.add(np.array([embedding]))
    
    doc_id = len(documents)
    documents.append({
        'id': doc_id,
        'filename': filename,
        'text': text,
        'embedding': embedding.tolist(),
        'timestamp': datetime.now().isoformat()
    })
    return doc_id

def search_documents(query, top_k=5):
    clean_query = preprocess_text(query)
    query_embedding = embedding_model.encode([clean_query])
    
    distances, indices = faiss_index.search(query_embedding, top_k)
    
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(documents):
            doc = documents[idx]
            results.append({
                'doc_id': doc['id'],
                'filename': doc['filename'],
                'score': float(distances[0][idx]),
                'excerpt': doc['text'][:200] + '...'
            })
    return results


def save_faiss_index(path):
    if faiss_index is not None:
        faiss.write_index(faiss_index, path)