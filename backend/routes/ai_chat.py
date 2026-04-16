"""
AI Chat Endpoint — FastAPI Router version.
Provides a streaming /api/ai/chat route connecting the RAG pipeline.
"""

import json
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
from backend.ai.groq_client import stream_chat_completion
from backend.ai.vector_store import search_documents

router = APIRouter()

async def generate_rag_response(query: str, history: List[Dict], user_role: str):
    """
    RAG orchestrated logic: Process query, search vector db, build context, call LLM.
    Native FastAPI async generator for streaming.
    """
    
    # 1. Search Vector DB for context
    try:
        search_results = search_documents(query, n_results=3)
        context_chunks = search_results.get("documents", [[]])[0]
        context_text = "\n\n".join(context_chunks)
    except Exception as e:
        print(f"Vector search failed: {e}")
        context_text = ""

    # 2. Construct System Prompt
    system_prompt = f"""You are the RESOLVIT Intelligent Assistant, acting as a smart digital case intake officer.
User role: {user_role}. 

# Core Responsibilities:
1. Explain RESOLVIT using provided context.
2. Trigger [WORKFLOW:COMPLAINT] if a civic problem is reported.

Context:
{context_text}
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": query})

    # 3. Stream from Groq
    try:
        print(f"🤖 Starting RAG stream for query: {query[:40]}...")
        async for chunk in stream_chat_completion(messages):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
        print("✅ Stream completed successfully")
    except Exception as e:
        print(f"❌ Stream failed: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@router.post("/chat")
async def chat_endpoint(request: Request, payload: dict = Body(...)):
    """
    Unified AI Chat Endpoint.
    """
    try:
        query = payload.get("message")
        history = payload.get("history", [])
        
        if not query:
            raise HTTPException(status_code=400, detail="Message is required")
            
        # User info from middleware (to be implemented in auth_decorator.py)
        user = getattr(request.state, "user", None)
        user_role = user.get("role", "citizen") if user else "citizen"
        
        return StreamingResponse(
            generate_rag_response(query, history, user_role=user_role),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"🔥 Chat endpoint crashed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
