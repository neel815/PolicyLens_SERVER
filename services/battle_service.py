"""Service for policy battle using Groq API"""

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
    
    # STEP A: Setup Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured.")
    
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
    
    # STEP D: Call Groq
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict insurance policy judge. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI battle failed: {str(e)[:120]}. Please try again."
        )
    
    # STEP E: Parse response
    if not response or not response.choices or len(response.choices) == 0:
        raise HTTPException(status_code=500, detail="AI returned empty response.")
    
    raw_response = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]
    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]
    
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]
    
    raw_response = raw_response.strip()
    
    # Extract JSON from response (handles extra text before/after)
    json_start = raw_response.find("{")
    json_end = raw_response.rfind("}")
    
    if json_start == -1 or json_end == -1:
        print(f"❌ No JSON object found in response: {raw_response[:200]}")
        raise HTTPException(
            status_code=500,
            detail="AI response did not contain valid JSON. Please try again."
        )
    
    # Extract just the JSON portion
    raw_response = raw_response[json_start:json_end + 1]
    
    # Clean up common JSON issues
    # Fix escaped newlines in strings by replacing with spaces
    raw_response = raw_response.replace('\\n', ' ')
    raw_response = raw_response.replace('\n', ' ')
    
    # Remove any null bytes or other problematic characters
    raw_response = raw_response.replace('\x00', '')
    
    # Fix common quote issues (straight quotes for valid JSON)
    raw_response = raw_response.replace('"', '"').replace('"', '"')  # smartquotes to straight
    raw_response = raw_response.replace(''', "'").replace(''', "'")  # smartsingle to straight
    
    print(f"✓ Raw Groq response extracted ({len(raw_response)} chars)")
    
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {str(e)}")
        print(f"Failed near position {e.pos}: {raw_response[max(0, e.pos-50):e.pos+100]}")
        
        # Try to fix common issues
        try:
            # Try to fix unescaped quotes in strings
            import re
            # This is a last-resort attempt to fix the JSON
            fixed = re.sub(r'(?<=[a-zA-Z0-9])"(?=[a-zA-Z0-9])', '\\"', raw_response)
            result = json.loads(fixed)
            print("✓ Fixed JSON after quote escaping")
        except:
            raise HTTPException(
                status_code=500,
                detail=f"AI response was not valid JSON: {str(e)[:80]}"
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
