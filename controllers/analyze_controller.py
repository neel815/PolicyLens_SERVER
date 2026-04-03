"""Controller for policy analysis - handles request validation and processing"""

from fastapi import UploadFile, HTTPException
from validators.file_validator import validate_pdf_upload
from services.analyze_service import analyze_policy_service


async def analyze_policy_controller(file: UploadFile) -> dict:
    """
    Process policy analysis request.
    
    Validates file, extracts PDF bytes, and calls analysis service.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        {"success": True, "data": {analysis results}}
        
    Raises:
        HTTPException: If validation or analysis fails
    """
    try:
        # Step 1: Validate file
        await validate_pdf_upload(file)
        
        # Step 2: Read file bytes
        pdf_bytes = await file.read()
        
        # Step 3: Reset file pointer
        await file.seek(0)
        
        # Step 4: Analyze policy (sync function)
        result = analyze_policy_service(pdf_bytes)
        
        # Step 5: Return success response
        return {
            "success": True,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
