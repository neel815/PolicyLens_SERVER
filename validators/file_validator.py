"""File validators for policy upload"""

import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (increased from 10MB for flexibility)
ALLOWED_EXTENSIONS = [".pdf"]
ALLOWED_CONTENT_TYPES = ["application/pdf"]
PDF_MAGIC_BYTES = b'%PDF'


async def validate_pdf_upload(file: UploadFile) -> bytes:
    """
    Validate uploaded PDF file with comprehensive checks.
    
    Validation steps:
    1. File exists and has filename
    2. Filename ends with .pdf (case-insensitive)
    3. Content type is application/pdf
    4. File size <= 50MB
    5. File magic bytes match PDF format (%PDF)
    6. PDF is not corrupted (can be parsed)
    
    Args:
        file: Uploaded file to validate
        
    Returns:
        bytes: File contents if validation succeeds
        
    Raises:
        HTTPException: If validation fails
    """
    # Check 1: File exists and has filename
    if not file or not file.filename:
        logger.warning("File upload: No file or filename provided")
        raise HTTPException(status_code=400, detail="No file provided.")
    
    # Check 2: File extension must be .pdf
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logger.warning(f"File upload: Invalid extension for file {file.filename}")
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are accepted."
        )
    
    # Check 3: Content type should be application/pdf
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(f"File upload: Invalid content type {file.content_type}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a PDF file."
        )
    
    # Read file contents
    contents = await file.read()
    
    # Check 4: File size must be <= MAX_FILE_SIZE
    if len(contents) > MAX_FILE_SIZE:
        logger.warning(f"File upload: File too large ({len(contents)} bytes)")
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB."
        )
    
    # Check 5: File must not be empty
    if len(contents) == 0:
        logger.warning("File upload: Empty file provided")
        raise HTTPException(
            status_code=400, 
            detail="File is empty. Please upload a valid PDF."
        )
    
    # Check 6: Validate PDF magic bytes
    if not contents.startswith(PDF_MAGIC_BYTES):
        logger.warning(f"File upload: Invalid PDF magic bytes")
        raise HTTPException(
            status_code=400, 
            detail="Invalid PDF file. File does not start with PDF magic bytes."
        )
    
    # Check 7: Try to parse PDF to ensure it's not corrupted
    try:
        from PyPDF2 import PdfReader
        import io
        
        pdf_reader = PdfReader(io.BytesIO(contents))
        
        if len(pdf_reader.pages) == 0:
            logger.warning("File upload: PDF has no pages")
            raise HTTPException(
                status_code=400, 
                detail="PDF has no pages. Please upload a valid policy document."
            )
        
        logger.info(f"File upload: Valid PDF with {len(pdf_reader.pages)} pages")
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"File upload: PDF parsing error: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot read PDF file. Please ensure it's a valid PDF document."
        )
    
    # Reset file pointer for later reading
    await file.seek(0)
    
    return contents

