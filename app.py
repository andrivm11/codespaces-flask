from app import create_app
from app.services.vector_store import save_faiss_index

app = create_app()

if __name__ == '__main__':
    try:
        print("begin")
        app.run(host='0.0.0.0', port=5000)
    finally:
        save_faiss_index(app.config['FAISS_INDEX_PATH'])
