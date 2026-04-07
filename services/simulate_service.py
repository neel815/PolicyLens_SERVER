"""Service for claim simulation using Groq API"""

import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from fastapi import HTTPException

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)


def simulate_claim_service(scenario: str, analysis: dict) -> dict:
    """
    Simulate a claim scenario against an insurance policy analysis.
    Uses Google Gemini to evaluate the likelihood of claim approval.
    
    Args:
        scenario: Detailed description of the claim scenario
        analysis: Policy analysis data with coverage, exclusions, risky clauses
        
    Returns:
        Dictionary with approval_chance, verdict, covered_aspects, 
        not_covered_aspects, risks, documents_needed, reasoning
        
    Raises:
        HTTPException: If simulation fails or AI analysis cannot be performed
    """
    # STEP A: Setup Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured.")
    
    # STEP B: Build analysis summary string
    policy_type = analysis.get("policy_type", "Insurance")
    coverage_score = analysis.get("coverage_score", "N/A")
    covered_events = analysis.get("covered_events", [])
    exclusions = analysis.get("exclusions", [])
    risky_clauses = analysis.get("risky_clauses", [])
    
    analysis_summary = f"""Policy Type: {policy_type}
Coverage Score: {coverage_score}/10

What is covered:
{chr(10).join(f'- {item}' for item in covered_events)}

What is NOT covered (exclusions):
{chr(10).join(f'- {item}' for item in exclusions)}

Risky clauses to note:
{chr(10).join(f'- {item}' for item in risky_clauses)}"""
    
    # STEP C: Build prompt
    prompt = f"""You are a strict insurance claim evaluator for Indian insurance policies.

Based on this policy analysis:
{analysis_summary}

Evaluate this claim scenario:
"{scenario}"

Return ONLY a raw JSON object. No markdown. No explanation. No code blocks.

Return exactly this structure:
{{
  "approval_chance": <integer 0-100>,
  "verdict": "<Likely Approved / Likely Rejected / Partial Coverage / Unclear>",
  "covered_aspects": [
    "<specific part of scenario that IS covered>"
  ],
  "not_covered_aspects": [
    "<specific part of scenario that is NOT covered>"
  ],
  "risks": [
    "<specific risk or condition that could affect this claim>"
  ],
  "documents_needed": [
    "<specific document needed to file this claim>"
  ],
  "reasoning": "<2-3 sentences explaining the verdict in plain English>"
}}

Rules:
- approval_chance: 0-100 integer only
- verdict must be exactly one of the 4 options listed
- Be strict — check exclusions carefully
- Be specific to THIS scenario and THIS policy
- covered_aspects: 1-4 items
- not_covered_aspects: 0-4 items (empty array if fully covered)
- risks: 1-3 items
- documents_needed: 2-5 specific documents for this claim type
- reasoning: plain English, no jargon, max 3 sentences
- Return ONLY raw JSON"""
    
    # STEP D: Call Groq API
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict insurance claim evaluator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI simulation failed: {str(e)[:120]}. Please try again."
        )
    
    # STEP E: Parse response
    if not response or not response.choices or len(response.choices) == 0:
        raise HTTPException(status_code=500, detail="AI returned empty response.")
    
    raw_text = response.choices[0].message.content.strip()
    print(f"Raw Groq response (first 500 chars): {repr(raw_text[:500])}")
    
    try:
        # Try direct JSON parse first
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        # If direct parse fails, try to extract JSON from markdown code blocks
        print(f"Direct JSON parse failed: {e}")
        
        # Try to find JSON between ``` markers (markdown code blocks)
        if "```json" in raw_text:
            start = raw_text.find("```json") + 7
            end = raw_text.find("```", start)
            if end != -1:
                json_str = raw_text[start:end].strip()
                try:
                    result = json.loads(json_str)
                    print("Successfully extracted JSON from markdown block")
                except json.JSONDecodeError:
                    print(f"Failed to parse extracted JSON: {json_str[:200]}")
                    raise HTTPException(status_code=500, detail="Could not extract valid JSON from response.")
            else:
                raise HTTPException(status_code=500, detail="Malformed JSON in response.")
        else:
            # Try to find raw JSON object { ... }
            json_start = raw_text.find('{')
            json_end = raw_text.rfind('}')
            if json_start != -1 and json_end != -1:
                json_str = raw_text[json_start:json_end + 1]
                try:
                    result = json.loads(json_str)
                    print("Successfully extracted JSON from raw text")
                except json.JSONDecodeError:
                    print(f"Failed to parse extracted raw JSON: {json_str[:200]}")
                    raise HTTPException(status_code=500, detail="Could not extract valid JSON from response.")
            else:
                raise HTTPException(status_code=500, detail="AI response was not valid JSON.")
    
    # STEP F: Validate required fields
    required = [
        "approval_chance", "verdict", "covered_aspects",
        "not_covered_aspects", "risks", "documents_needed", "reasoning"
    ]
    for key in required:
        if key not in result:
            raise HTTPException(status_code=500, detail=f"Missing field: {key}")
    
    # Validate approval_chance
    chance = result["approval_chance"]
    if isinstance(chance, float):
        chance = int(chance)
    if not isinstance(chance, int) or not (0 <= chance <= 100):
        raise HTTPException(status_code=500, detail="Invalid approval_chance value.")
    result["approval_chance"] = chance
    
    # STEP G: Return
    return {
        "approval_chance": result["approval_chance"],
        "verdict": result["verdict"],
        "covered_aspects": result["covered_aspects"],
        "not_covered_aspects": result["not_covered_aspects"],
        "risks": result["risks"],
        "documents_needed": result["documents_needed"],
        "reasoning": result["reasoning"]
    }
