from flask import Flask
from .config import Config
from .routes.documents import documents_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize components
    from app.services.vector_store import initialize_faiss
    from app.services.knowledge_graph import initialize_neo4j
    
    initialize_faiss(app)
    initialize_neo4j(app)

    # Register blueprints
    app.register_blueprint(documents_bp)

    return app