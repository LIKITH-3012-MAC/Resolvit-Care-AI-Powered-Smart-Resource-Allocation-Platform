"""
AI Chat Endpoint
Provides a streaming /api/ai/chat route connecting the RAG pipeline.
"""

import json
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.routes.auth import get_current_user
from backend.app.ai.groq_client import stream_chat_completion
from backend.app.ai.vector_store import search_documents

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # Expected Format: [{"role": "user", "content": "..."}, ...]
    
async def generate_rag_response(query: str, history: list[dict], user_role: str):
    """
    RAG orchestrated logic: Process query, search vector db, build context, call LLM
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
    system_prompt = f"""You are the RESOLVIT Intelligent Assistant, acting as a smart digital case intake officer, support guide, and project-aware AI explicitly for the RESOLVIT civic resolution platform.
You are currently addressing a user with the role of: {user_role}. 

# Core Responsibilities:
1. **Explain the Platform**: If the user asks about RESOLVIT, use the provided context to explain it clearly.
2. **Guide Complaints**: If the user indicates they want to raise a complaint, report an issue, or ask for help regarding a civic problem, you MUST trigger the structural intake workflow.
3. **Be Conversational**: Answer naturally and helpfully. Keep answers concise.

# CRITICAL ROUTING INSTRUCTION:
If the user explicitly requests to file a complaint, report an issue, or if their message describes a civic problem that clearly needs to be recorded (like "There is a water leak" or "Broken streetlights"), you must IMMEDIATELY respond with precisely this exact token:

[WORKFLOW:COMPLAINT]

Do not provide conversational text alongside this token if you trigger it. The frontend UI will intercept this token and display the structured intake form.

Retrieved Platform Context:
{context_text}
"""
    
    # 3. Assemble messages for LLM
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history (limit to last 10 messages to save context window)
    for msg in history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": query})

    # 4. Stream response
    try:
        async for chunk in stream_chat_completion(messages):
            # Stream token wrapped in SSE format if needed, but for simplicity raw text streaming or JSON per line
            # Many frontends expect JSON per line or Server-Sent Events
            yield f"data: {json.dumps({'content': chunk})}\n\n"
            
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@router.post("/chat")
async def chat_endpoint(req: ChatRequest, user=Depends(get_current_user)):
    """
    Open chat endpoint taking message and optional history.
    Streams back LLM tokens.
    """
    return StreamingResponse(
        generate_rag_response(req.message, req.history, user_role=user.get("role", "citizen")),
        media_type="text/event-stream"
    )
