"""
AI Document Ingestion Endpoint — Flask Blueprint version.
Handles uploading PDFs, DOCX, and CSVs into the ChromaDB vector store.
"""

import uuid
from flask import Blueprint, request, jsonify, g
from backend.auth_decorator import token_required
from backend.app.ai.document_parser import parse_pdf, parse_docx, parse_csv
from backend.app.ai.vector_store import add_documents

ai_ingest_bp = Blueprint('ai_ingest_bp', __name__)

@ai_ingest_bp.route("/ingest", methods=["POST"])
@token_required
async def ingest_document():
    """
    Upload a document, parse text, generate embeddings, and store in ChromaDB.
    """
    user = g.current_user
    
    # Restrict to admins or specific roles
    if user.get("role") not in ["admin", "coordinator"]:
        return jsonify({"error": "Only admins or coordinators can ingest knowledge."}), 403
        
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    file_bytes = file.read()
    filename = file.filename.lower()
    
    text_chunks = []
    
    # Route to parser
    if filename.endswith(".pdf"):
        text_chunks = parse_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text_chunks = parse_docx(file_bytes)
    elif filename.endswith(".csv"):
        text_chunks = parse_csv(file_bytes, file.filename)
    else:
        return jsonify({"error": "Unsupported file format. Please upload PDF, DOCX, or CSV."}), 400

    if not text_chunks:
        return jsonify({"error": "No readable text found in document."}), 400
        
    # Generate random UUIDs for chunks
    doc_ids = [str(uuid.uuid4()) for _ in text_chunks]
    
    # Store metadata for tracking provenance
    metadatas = [
        {
            "source": file.filename, 
            "uploader_id": str(user.get("id")),
            "chunk_index": i
        } for i in range(len(text_chunks))
    ]
    
    # Add to ChromaDB
    try:
        add_documents(
            texts=text_chunks,
            metadatas=metadatas,
            ids=doc_ids,
            collection_name="knowledge_base"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to index document: {str(e)}"}), 500

    return jsonify({
        "message": f"Successfully ingested {file.filename}",
        "chunks_indexed": len(text_chunks)
    })
