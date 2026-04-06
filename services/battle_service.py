"""Service for policy battle using Google Gemini"""

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


def build_summary(analysis: dict, name: str) -> str:
    """Build a summary string for a policy."""
    return f"""Policy: {name}
Type: {analysis.get('policy_type', 'Insurance')}
Coverage Score: {analysis.get('coverage_score', 0)}/10

Covered:
{chr(10).join(f"- {e}" for e in analysis.get('covered_events', []))}

Exclusions:
{chr(10).join(f"- {e}" for e in analysis.get('exclusions', []))}

Risky Clauses:
{chr(10).join(f"- {e}" for e in analysis.get('risky_clauses', []))}
"""


def battle_service(
    analysis1: dict, name1: str,
    analysis2: dict, name2: str
) -> dict:
    """
    Battle two insurance policies using Gemini AI.
    
    Compares policies across 6 categories and returns detailed results.
    
    Args:
        analysis1: Analysis data for policy 1
        name1: Name/filename of policy 1
        analysis2: Analysis data for policy 2
        name2: Name/filename of policy 2
        
    Returns:
        Battle results with rounds, scores, and verdict
        
    Raises:
        HTTPException: If Gemini API call fails or response is invalid
    """
    
    # STEP A: Setup Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
    
    genai.configure(api_key=api_key)
    
    # STEP B: Build summaries
    summary1 = build_summary(analysis1, name1)
    summary2 = build_summary(analysis2, name2)
    
    # STEP C: Build prompt
    prompt = f"""You are a strict insurance policy judge.

Compare these two insurance policies head to head across
exactly 6 categories. Be analytical and specific.

POLICY A:
{summary1}

POLICY B:
{summary2}

Judge them across these 6 categories and pick a winner for each:
1. Coverage breadth — which covers more scenarios
2. Exclusions — which has fewer/fairer exclusions
3. Value for money — based on coverage score and terms
4. Claim friendliness — which is easier to claim from
5. Transparency — which has clearer, less tricky language
6. Overall protection — which gives better real-world protection

IMPORTANT: Return ONLY a raw JSON object. Do not wrap it in markdown code blocks.
Do not include any text before or after the JSON. Start directly with {{ and end with }}.

{{
  "policy_a_name": "{name1}",
  "policy_b_name": "{name2}",
  "rounds": [
    {{
      "category": "Coverage breadth",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }},
    {{
      "category": "Exclusions",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }},
    {{
      "category": "Value for money",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }},
    {{
      "category": "Claim friendliness",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }},
    {{
      "category": "Transparency",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }},
    {{
      "category": "Overall protection",
      "winner": "A" or "B" or "Draw",
      "score_a": <integer 0-10>,
      "score_b": <integer 0-10>,
      "reasoning": "<one sentence why>"
    }}
  ],
  "overall_winner": "A" or "B" or "Draw",
  "final_score_a": <integer — count of rounds won by A>,
  "final_score_b": <integer — count of rounds won by B>,
  "verdict": "<2-3 sentences final verdict in plain English>",
  "policy_a_best_for": "<one sentence — what type of person/situation Policy A suits>",
  "policy_b_best_for": "<one sentence — what type of person/situation Policy B suits>"
}}

Rules:
- winner must be exactly "A", "B", or "Draw"
- overall_winner must be exactly "A", "B", or "Draw"
- score_a and score_b must be integers 0-10
- final_score_a + final_score_b must equal 6 (draws count for both)
- Be specific — mention actual policy details in reasoning
- Return ONLY the JSON object with no markdown, no code blocks, no explanation"""
    
    # STEP D: Call Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 1,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI battle failed: {str(e)[:120]}. Please try again."
        )
    
    # STEP E: Parse response
    if not response or not hasattr(response, 'text') or not response.text:
        raise HTTPException(status_code=500, detail="AI returned empty response.")
    
    raw_response = response.text.strip()
    
    # Handle markdown code blocks that Gemini sometimes returns
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]  # Remove ```json
    if raw_response.startswith("```"):
        raw_response = raw_response[3:]  # Remove ```
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]  # Remove closing ```
    
    raw_response = raw_response.strip()
    
    # Check if response looks incomplete (common Gemini issue)
    if not raw_response.endswith("}"):
        # Try to find the last complete closing brace
        last_brace = raw_response.rfind("}")
        if last_brace == -1:
            print(f"❌ Incomplete JSON response (no closing brace): {raw_response[:200]}")
            raise HTTPException(
                status_code=500,
                detail="AI response was incomplete. Please try the battle again."
            )
        # Truncate to last complete object
        raw_response = raw_response[:last_brace + 1]
    
    # Debug: print raw response
    print(f"✓ Raw Gemini response parsed successfully ({len(raw_response)} chars)")
    
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {str(e)}")
        print(f"Failed at: {raw_response[max(0, e.pos-50):e.pos+50]}")
        raise HTTPException(
            status_code=500,
            detail=f"AI response was not valid JSON: {str(e)[:100]}"
        )
    
    # STEP F: Validate result
    required = [
        "rounds", "overall_winner", "final_score_a",
        "final_score_b", "verdict", "policy_a_best_for",
        "policy_b_best_for"
    ]
    for key in required:
        if key not in result:
            raise HTTPException(status_code=500, detail=f"Missing field: {key}")
    
    if len(result["rounds"]) != 6:
        raise HTTPException(status_code=500, detail="Expected 6 battle rounds.")
    
    # STEP G: Return result
    return result
