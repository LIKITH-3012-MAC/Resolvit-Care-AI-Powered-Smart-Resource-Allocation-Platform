"""
Document Parsing Utility
Provides functions to extract and chunk text from common document types like PDF, DOCX, and CSV.
"""
import csv
import io
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
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks

def parse_pdf(file_bytes: bytes) -> list[str]:
    """Extract and chunk text from a PDF file."""
    text_chunks = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                text_chunks.extend(_chunk_text(text))
        doc.close()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text_chunks

def parse_docx(file_bytes: bytes) -> list[str]:
    """Extract and chunk text from an MS Word DOCX file."""
    text_chunks = []
    try:
        doc = Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        text_chunks.extend(_chunk_text("\n".join(full_text)))
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
    return text_chunks

def parse_csv(file_bytes: bytes, filename: str = "data.csv") -> list[str]:
    """
    Extract rows from a CSV as JSON-like textual chunks using built-in csv module.
    """
    text_chunks = []
    try:
        stream = io.StringIO(file_bytes.decode("utf-8"))
        reader = csv.DictReader(stream)
        for idx, row in enumerate(reader):
            # E.g. "Row 0 from data.csv: {'Name': 'John', 'Age': '30'}"
            row_str = f"Row {idx} from {filename}: {str(row)}"
            text_chunks.append(row_str)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
    return text_chunks
