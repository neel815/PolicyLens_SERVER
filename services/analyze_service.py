"""Service for policy analysis using Google Gemini"""

import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException
from utils.pdf_utils import extract_text_from_pdf

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)


def analyze_policy_service(pdf_bytes: bytes) -> dict:
    """
    Analyze insurance policy PDF using Google Gemini API.
    
    Single unified call to:
    1. Validate that document is an insurance/coverage document
    2. Analyze and extract coverage, exclusions, risky clauses
    3. Works for ANY insurance type (health, car, home, cyber, marine, etc)
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Dictionary with covered_events, exclusions, risky_clauses, coverage_score, policy_type, score_reason
        
    Raises:
        HTTPException: If PDF is invalid, not insurance, or AI analysis fails
    """
    # STEP A: Extract text from PDF
    try:
        text = extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    policy_text = text[:8000]
    
    # STEP B: Setup Gemini client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
    
    genai.configure(api_key=api_key)
    
    # STEP C: Build smart universal prompt (one call: validate + analyze)
    analysis_prompt = f"""You are an expert insurance analyst.

First, determine if the following document is any kind of 
insurance policy, warranty, indemnity, or coverage agreement.
This includes but is not limited to: health, life, car, home,
travel, pet, marine, cyber, business, event, crop, machinery,
showroom, product liability, professional indemnity, 
fire, burglary, or any other insurance type.

If it IS an insurance document:
Analyze it carefully and return this exact JSON:
{{
  "is_insurance": true,
  "policy_type": "<detected type e.g. Health / Car / Showroom / Marine / Cyber>",
  "covered_events": [
    "<specific thing covered, plain English>",
    "<specific thing covered>",
    "<specific thing covered>"
  ],
  "exclusions": [
    "<specific thing NOT covered>",
    "<specific thing NOT covered>"
  ],
  "risky_clauses": [
    "<important clause user must know>",
    "<important clause>"
  ],
  "coverage_score": <integer 0-10>,
  "score_reason": "<one sentence explaining the score>"
}}

If it is NOT an insurance document:
Return exactly:
{{
  "is_insurance": false,
  "policy_type": null,
  "covered_events": [],
  "exclusions": [],
  "risky_clauses": [],
  "coverage_score": 0,
  "score_reason": "Document is not an insurance policy"
}}

Rules:
- Be specific to THIS document — no generic answers
- covered_events: 3 to 6 items
- exclusions: 2 to 5 items
- risky_clauses: 2 to 4 items
- coverage_score: honest rating of how comprehensive this policy is
- Plain English only — no legal jargon
- Return ONLY raw JSON — no markdown, no code blocks, no explanation

Document:
{policy_text}"""
    
    # STEP D: Call Gemini API
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            analysis_prompt,
            generation_config={
                "temperature": 1,
                "max_output_tokens": 4000,
                "response_mime_type": "application/json",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)[:120]}. Please try again."
        )
    
    # STEP E: Parse response
    if not response or not hasattr(response, 'text') or not response.text:
        raise HTTPException(
            status_code=500,
            detail="AI returned empty response. Please try again."
        )
    
    try:
        result = json.loads(response.text.strip())
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response (first 300 chars): {repr(response.text[:300])}")
        raise HTTPException(
            status_code=500,
            detail="AI response was not valid JSON. Please try again."
        )
    
    # STEP F: Check if document is insurance
    if not result.get("is_insurance", False):
        raise HTTPException(
            status_code=400,
            detail="This document does not appear to be an insurance policy. "
                   "Please upload a valid insurance, warranty, or coverage document."
        )
    
    # STEP G: Validate required keys exist
    required_keys = [
        "covered_events",
        "exclusions",
        "risky_clauses",
        "coverage_score"
    ]
    for key in required_keys:
        if key not in result:
            raise HTTPException(
                status_code=500,
                detail=f"Incomplete AI response: missing '{key}'. Please try again."
            )
    
    # Validate arrays are non-empty lists
    for key in ["covered_events", "exclusions", "risky_clauses"]:
        if not isinstance(result[key], list) or len(result[key]) == 0:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid response: '{key}' must be a non-empty list."
            )
    
    # Validate and normalize coverage_score
    score = result["coverage_score"]
    if isinstance(score, float):
        score = int(score)
    if not isinstance(score, int) or not (0 <= score <= 10):
        raise HTTPException(
            status_code=500,
            detail="Invalid coverage score returned by AI."
        )
    result["coverage_score"] = score
    
    # STEP H: Return clean result for frontend
    return {
        "covered_events": result["covered_events"],
        "exclusions": result["exclusions"],
        "risky_clauses": result["risky_clauses"],
        "coverage_score": result["coverage_score"],
        "policy_type": result.get("policy_type", "Insurance"),
        "score_reason": result.get("score_reason", "")
    }
