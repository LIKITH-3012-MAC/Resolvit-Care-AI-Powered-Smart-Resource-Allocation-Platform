"""
Vector Store Connection
Wrapper around ChromaDB for local persistent vector storage and retrieval.
"""

import os
from pathlib import Path
import chromadb
from chromadb.config import Settings

from backend.app.ai.embeddings import generate_embeddings

# Persistent directory for ChromaDB within the backend package
DB_PATH = str(Path(__file__).resolve().parent.parent.parent / "database" / "chroma_db")

# Initialize persistent client
_client = chromadb.PersistentClient(path=DB_PATH, settings=Settings(allow_reset=True))

def get_collection(collection_name: str = "knowledge_base"):
    """Get or create the main ChromaDB collection."""
    # We define a custom embedding function to adhere to Chroma's interface
    # but we use sentence-transformers from our embeddings.py
    
    class CustomEmbeddingFunction(chromadb.EmbeddingFunction):
        def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
            return generate_embeddings(input)

    collection = _client.get_or_create_collection(
        name=collection_name,
        embedding_function=CustomEmbeddingFunction()
    )
    return collection

def add_documents(texts: list[str], metadatas: list[dict], ids: list[str], collection_name: str = "knowledge_base"):
    """
    Add documents to the vector store.
    """
    collection = get_collection(collection_name)
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )

def search_documents(query: str, n_results: int = 5, collection_name: str = "knowledge_base"):
    """
    Search the vector store using a text query.
    Returns the top n_results.
    """
    collection = get_collection(collection_name)
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results
