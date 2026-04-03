"""PDF utilities for text extraction"""

import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using PyMuPDF (fitz).
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Combined text from all pages
        
    Raises:
        ValueError: If PDF cannot be read or is empty
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        text = text.strip()
        if not text:
            raise ValueError("Could not extract text. PDF may be scanned or image-based.")
        
        return text
    except fitz.FileError:
        raise ValueError("Failed to read PDF file.")
    except Exception:
        raise ValueError("Failed to read PDF file.")
