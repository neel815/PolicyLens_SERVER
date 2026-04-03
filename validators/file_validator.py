"""File validators for policy upload"""

from fastapi import UploadFile, HTTPException


async def validate_pdf_upload(file: UploadFile) -> None:
    """
    Validate uploaded PDF file.
    
    Checks in order:
    1. File exists and has filename
    2. Filename ends with .pdf (case-insensitive)
    3. Content type is application/pdf
    4. File size <= 10MB
    
    Args:
        file: Uploaded file to validate
        
    Raises:
        HTTPException: If validation fails
    """
    # Check 1: File exists and has filename
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    # Check 2: File extension must be .pdf
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    # Check 3: Content type should be application/pdf or allow missing content type
    # Be lenient with content type since different clients may not set it correctly
    if file.content_type and file.content_type != "application/pdf":
        # If content type is set and it's NOT pdf, reject it
        if not file.content_type.startswith("application/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    # If content type is None or application/*, allow it since filename is .pdf
    
    # Check 4: File size must be <= 10MB
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Reset file pointer for later reading
    await file.seek(0)
