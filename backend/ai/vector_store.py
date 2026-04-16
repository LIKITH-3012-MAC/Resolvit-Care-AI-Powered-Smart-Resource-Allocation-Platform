"""
Vector Store Shim — PostgreSQL Version
Replaces ChromaDB with a lightweight PostgreSQL table to fit within Render Free Tier.
"""

import json
import uuid
from backend.database import execute, fetch_all

def add_documents(texts: list[str], metadatas: list[dict], ids: list[str], collection_name: str = "knowledge_base"):
    """
    Add documents to the PostgreSQL knowledge base.
    """
    # Note: collection_name is ignored in this shim to keep it simple (single table)
    for i in range(len(texts)):
        doc_id = ids[i] if ids and i < len(ids) else str(uuid.uuid4())
        meta = json.dumps(metadatas[i]) if metadatas and i < len(metadatas) else "{}"
        
        # Using a fire-and-forget approach for each doc in this shim
        # In production, use a batch insert
        import asyncio
        asyncio.create_task(execute(
            "INSERT INTO knowledge_base (id, content, metadata) VALUES ($1, $2, $3) ON CONFLICT (id) DO UPDATE SET content = $2, metadata = $3",
            uuid.UUID(doc_id), texts[i], meta
        ))

async def search_documents(query: str, n_results: int = 5, collection_name: str = "knowledge_base"):
    """
    Search the PostgreSQL knowledge base using text matching (ILIKE).
    """
    # Simple keyword search for Render Free Tier
    # In a full deployment, use pgvector or FTS
    search_query = f"%{query}%"
    rows = await fetch_all(
        "SELECT content, metadata FROM knowledge_base WHERE content ILIKE $1 LIMIT $2",
        search_query, n_results
    )
    
    # Format to match the expected return structure of the previously used ChromaDB
    return {
        "documents": [[r["content"] for r in rows]],
        "metadatas": [[r["metadata"] for r in rows]]
    }
