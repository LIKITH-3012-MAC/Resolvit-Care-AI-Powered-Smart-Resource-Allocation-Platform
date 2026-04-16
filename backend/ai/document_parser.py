"""
Document Parsing Utility
Provides functions to extract and chunk text from common document types like PDF, DOCX, and CSV.
"""
import io
import pandas as pd
import fitz  # PyMuPDF
from docx import Document

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Naively split text into overlapping chunks based on word count.
    """
    words = text.split()
    chunks = []
    
    if not words:
        return chunks
        
    start = 0
    while start < len(words):
        # The end index is either start + chunk_size, or the end of the list
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        
        # Move start forward
        start += (chunk_size - overlap)
        
    return chunks

def parse_pdf(file_bytes: bytes) -> list[str]:
    """Extract and chunk text from a PDF file."""
    text_chunks = []
    try:
        # Load PDF from memory
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                # Append chunks from this page
                text_chunks.extend(_chunk_text(text))
        doc.close()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text_chunks

def parse_docx(file_bytes: bytes) -> list[str]:
    """Extract and chunk text from an MS Word DOCX file."""
    text_chunks = []
    try:
        # Load Docx from memory
        doc = Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
                
        # Join and split
        text_chunks.extend(_chunk_text("\n".join(full_text)))
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
    return text_chunks

def parse_csv(file_bytes: bytes, filename: str = "data.csv") -> list[str]:
    """
    Extract rows from a CSV as JSON-like textual chunks 
    so the embedding model understands tabular relationships.
    """
    text_chunks = []
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        # Convert each row into a text string
        for idx, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            # E.g. "Row 0 from data.csv: {'Name': 'John', 'Age': 30}"
            row_str = f"Row {idx} from {filename}: {str(row_dict)}"
            text_chunks.append(row_str)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
    return text_chunks
