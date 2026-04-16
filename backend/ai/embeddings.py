"""
Text Embedding Service
Lightweight version for Render Free Tier.
Provides zero-vector placeholders to satisfy the interface without loading heavy models.
"""

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Returns placeholder embeddings (zero vectors).
    In the Lean Architecture, we rely on text matching in the Vector Store.
    """
    if not texts:
        return []
    
    # Return 384-dimensional zero vectors (MiniLM size) to maintain contract
    return [[0.0] * 384 for _ in texts]
