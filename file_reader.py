import os
from pathlib import Path

def extract_text(file_path: str, max_chars=5000) -> str:
    """
    Safely reads a file (txt, pdf, docx) and extracts its text up to max_chars.
    Returns an empty string if it cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        return ""
        
    ext = path.suffix.lower()
    text = ""
    
    try:
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(max_chars)
                
        elif ext == '.pdf':
            try:
                import PyPDF2
                with open(path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + " "
                        if len(text) >= max_chars:
                            break
            except ImportError:
                print("Warning: PyPDF2 is not installed.")
                
        elif ext in ['.doc', '.docx']:
            try:
                from docx import Document
                doc = Document(path)
                for para in doc.paragraphs:
                    text += para.text + " "
                    if len(text) >= max_chars:
                        break
            except ImportError:
                print("Warning: python-docx is not installed.")
                
    except Exception as e:
        # We fail silently and return whatever we got if the file is corrupted
        pass
        
    return text.strip().lower()[:max_chars]
