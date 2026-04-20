"""Service for chat with policy using Google Gemini"""

import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)


def chat_policy_service(question: str, analysis: dict) -> dict:
    """
    Chat with an insurance policy using Gemini AI.
    
    Args:
        question: User's question about the policy
        analysis: Policy analysis data with coverage, exclusions, etc
        
    Returns:
        Chat response with answer, confidence, metadata
        
    Raises:
        HTTPException: If Gemini API call fails or response is invalid
    """
    
    # STEP A: Setup Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
    
    genai.configure(api_key=api_key)
    
    # STEP B: Build analysis summary
    analysis_summary = f"""Policy Type: {analysis.get('policy_type', 'Insurance')}
    Coverage Score: {analysis.get('coverage_score', 0)}/10
    Score Reason: {analysis.get('score_reason', '')}

    What is covered:
    {chr(10).join(f"- {e}" for e in analysis.get('covered_events', []))}

    What is NOT covered (exclusions):
    {chr(10).join(f"- {e}" for e in analysis.get('exclusions', []))}

    Risky clauses to be aware of:
    {chr(10).join(f"- {e}" for e in analysis.get('risky_clauses', []))}
    """
    
    # STEP C: Build prompt
    prompt = f"""You are a helpful insurance expert assistant.
    Answer the user's question based ONLY on the policy analysis below.
    Do not make up information that is not in the analysis.

    Policy Analysis:
    {analysis_summary}

    User Question: "{question}"

    Return ONLY a raw JSON object:
    {{
    "answer": "<clear, helpful answer in plain English>",
    "confidence": <integer 0-100>,
    "found_in_policy": true or false,
    "related_section": "<which section answers this — covered_events / exclusions / risky_clauses / general>"
    }}

    Rules:
    - answer: 1-3 sentences max, plain English, no jargon
    - confidence: how confident you are the answer is accurate (0-100)
    - found_in_policy: true if directly mentioned, false if inferred
    - If question cannot be answered from the analysis:
    answer: "This specific detail isn't clearly mentioned in your policy analysis. Consider reading the full policy document or contacting your insurer."
    confidence: 0
    found_in_policy: false
    - Return ONLY raw JSON, no markdown"""
    
    # STEP D: Call Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 1,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI chat failed: {str(e)[:120]}. Please try again."
        )
    
    # STEP E: Parse response
    if not response or not hasattr(response, 'text') or not response.text:
        raise HTTPException(status_code=500, detail="AI returned empty response.")
    
    try:
        result = json.loads(response.text.strip())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI response was not valid JSON.")
    
    # STEP F: Validate result
    required = ["answer", "confidence", "found_in_policy", "related_section"]
    for key in required:
        if key not in result:
            raise HTTPException(status_code=500, detail=f"Missing field: {key}")
    
    confidence = result["confidence"]
    if isinstance(confidence, float):
        confidence = int(confidence)
    if not isinstance(confidence, int) or not (0 <= confidence <= 100):
        result["confidence"] = 0
    result["confidence"] = confidence
    
    # STEP G: Return
    return {
        "answer": result["answer"],
        "confidence": result["confidence"],
        "found_in_policy": result["found_in_policy"],
        "related_section": result["related_section"]
    }
