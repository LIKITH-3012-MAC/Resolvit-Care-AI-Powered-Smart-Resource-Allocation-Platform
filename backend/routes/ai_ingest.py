"""
AI Document Ingestion Endpoint — FastAPI Router version.
Handles uploading PDFs, DOCX, and CSVs into the ChromaDB vector store.
"""

import uuid
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Depends
from backend.ai.document_parser import parse_pdf, parse_docx, parse_csv
from backend.ai.vector_store import add_documents

router = APIRouter()

@router.post("/ingest")
async def ingest_document(request: Request, file: UploadFile = File(...)):
    """
    Upload a document, parse text, generate embeddings, and store in ChromaDB.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Restrict to admins or specific roles
    if user.get("role") not in ["admin", "coordinator"]:
         raise HTTPException(status_code=403, detail="Only admins or coordinators can ingest knowledge.")
        
    filename = file.filename.lower()
    file_bytes = await file.read()
    
    text_chunks = []
    
    # Route to parser
    if filename.endswith(".pdf"):
        text_chunks = parse_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text_chunks = parse_docx(file_bytes)
    elif filename.endswith(".csv"):
        text_chunks = parse_csv(file_bytes, file.filename)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or CSV.")

    if not text_chunks:
        raise HTTPException(status_code=400, detail="No readable text found in document.")
        
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
         raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

    return {
        "message": f"Successfully ingested {file.filename}",
        "chunks_indexed": len(text_chunks)
    }
