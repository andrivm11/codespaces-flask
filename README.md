# Document Processing and Semantic Search API

A Flask-based API for document processing, semantic search, and knowledge graph integration using NLP techniques.

## Features

- Document processing for PDF, DOCX, and TXT files
- Text preprocessing (tokenization, lemmatization, stopword removal)
- Sentence embeddings using sentence-transformers
- Semantic search with FAISS index
- Knowledge graph integration with Neo4j
- Named Entity Recognition and relationship extraction
- REST API endpoints for easy integration

## Prerequisites

- Python 3.8+
- pip package manager
- Credentials for Neo4j
- spaCy English model: `en_core_web_sm`

### Install dependencies

```bash
pip install -r requirements.txt
```

### Download spacy model

```bash
python -m spacy download en_core_web_sm
```

### Run the application

```bash
python run.py
```

## To test the application

### Upload Document


```bash
curl -X POST -F "file=@factura.txt" http://localhost:5000/upload
```

### Semantic search


```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "factura", "top_k": 3}' \
  http://localhost:5000/search
```

### Get Document Entities



```bash
curl http://localhost:5000/entities/0
```

