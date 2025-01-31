import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    FAISS_INDEX_PATH = 'faiss_index.index'
    NEO4J_URI = "bolt://184.72.108.88:7687"
    NEO4J_AUTH = ("neo4j", "intents-possession-opposites")
    
    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)