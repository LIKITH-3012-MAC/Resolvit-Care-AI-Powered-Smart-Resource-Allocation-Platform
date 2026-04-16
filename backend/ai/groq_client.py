"""
Groq API Client Integration
Handles async connection to Groq for ultra-low latency inference.
"""

from groq import AsyncGroq
from backend.config import settings

# Initialize Async Groq Client
_client = AsyncGroq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

def get_groq_client() -> AsyncGroq:
    """Returns the configured AsyncGroq client."""
    if not _client:
        raise ValueError("GROQ_API_KEY not configured in environment.")
    return _client

async def stream_chat_completion(messages: list, model: str = "llama-3.3-70b-versatile"):
    """
    Generate an async streaming completion using Groq.
    
    Args:
        messages: List of message dictionaries (role, content)
        model: The Groq model to use
        
    Yields:
        str: Streaming content chunks
    """
    client = get_groq_client()
    stream = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
