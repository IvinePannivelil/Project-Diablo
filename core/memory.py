import chromadb
from chromadb.utils import embedding_functions
import os

class RAGMemory:
    def __init__(self, db_path="memory/chroma_db"):
        print("Initializing Diablo's Omniscient Memory (ChromaDB)...")
        os.makedirs(db_path, exist_ok=True)
        
        # Persistent local storage
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Local embedding model (runs completely offline)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Main memory collection
        self.collection = self.client.get_or_create_collection(
            name="diablo_core_memory",
            embedding_function=self.embedding_fn
        )
        print("Memory initialized successfully.")

    def ingest_text(self, text: str, source: str, doc_id: str):
        self.collection.add(
            documents=[text],
            metadatas=[{"source": source}],
            ids=[doc_id]
        )
        print(f"Ingested document: {source} into memory.")

    def search(self, query: str, n_results: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'] or len(results['documents'][0]) == 0:
            return []
            
        return results['documents'][0]

