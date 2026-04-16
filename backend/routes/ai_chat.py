"""
AI Chat Endpoint — Flask Blueprint version.
Provides a streaming /api/ai/chat route connecting the RAG pipeline.
"""

import json
import queue
import threading
import asyncio
from flask import Blueprint, request, Response, jsonify, g
from backend.auth_decorator import optional_token
from backend.app.ai.groq_client import stream_chat_completion
from backend.app.ai.vector_store import search_documents

ai_chat_bp = Blueprint('ai_chat_bp', __name__)

def generate_rag_response(query: str, history: list[dict], user_role: str):
    """
    RAG orchestrated logic: Process query, search vector db, build context, call LLM.
    Uses a threaded bridge to support sync Flask (WSGI) streaming of async generators.
    """
    
    # 1. Search Vector DB for context (Synchronous call to ChromaDB)
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

    # 3. Threaded Sync Bridge
    q = queue.Queue()
    
    def worker():
        # Create a fresh event loop for this thread to manage the async Groq stream
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_stream():
            try:
                print(f"🤖 Starting RAG stream for query: {query[:40]}...")
                async for chunk in stream_chat_completion(messages):
                    q.put(f"data: {json.dumps({'content': chunk})}\n\n")
                q.put("data: [DONE]\n\n")
                print("✅ Stream completed successfully")
            except Exception as e:
                print(f"❌ Stream failed: {e}")
                q.put(f"data: {json.dumps({'error': str(e)})}\n\n")
            finally:
                q.put(None) # Sentinel to close the sync generator
        
        loop.run_until_complete(run_stream())
        loop.close()

    # Start the async collection thread
    threading.Thread(target=worker, daemon=True).start()

    # Consuming sync generator
    while True:
        item = q.get()
        if item is None: break
        yield item

@ai_chat_bp.route("/chat", methods=["POST"])
@optional_token
async def chat_endpoint():
    """
    Unified AI Chat Endpoint.
    """
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400
            
        query = data["message"]
        history = data.get("history", [])
        
        # g.current_user set by optional_token decorator
        user_role = g.current_user.get("role", "citizen") if g.current_user else "citizen"
        
        # Return the sync-wrapped generator
        return Response(
            generate_rag_response(query, history, user_role=user_role),
            mimetype="text/event-stream"
        )
    except Exception as e:
        print(f"🔥 Chat endpoint crashed: {e}")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500
