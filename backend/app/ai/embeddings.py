"""
Text Embedding Service
Handles generating dense embeddings for text chunks using sentence-transformers.
"""

from sentence_transformers import SentenceTransformer

# Initialize the embedding model (downloads on first run)
# 'all-MiniLM-L6-v2' is fast, small and good for MVP
MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        # Load the model
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (list of floats)
    """
    if not texts:
        return []
    
    model = get_embedding_model()
    # encode returns a numpy array, convert to list
    embeddings = model.encode(texts)
    return embeddings.tolist()
