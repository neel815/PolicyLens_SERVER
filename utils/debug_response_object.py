import os
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from backend directory
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """Analyze this insurance policy text:

SAMPLE POLICY DOCUMENT
Policyholder: John Doe
Policy Number: INS-2024-12345
Premium: $500/month
Coverage: Medical expenses, dental, vision
Exclusions: Pre-existing conditions, cosmetic procedures
Claims Process: Submit within 30 days
Coverage Score: 8/10

Return ONLY a valid JSON object with these exact fields:
{
  "covered_events": [list of covered events],
  "exclusions": [list of exclusions],
  "risky_clauses": [list of risky clauses],
  "coverage_score": number between 0 and 10
}"""

response = model.generate_content(
    prompt,
    request_options={"timeout": 45}
)

print(f"=== RESPONSE OBJECT ATTRIBUTES ===")
print(f"Type: {type(response)}")
print(f"Dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")

print(f"\n=== TRYING DIFFERENT WAYS TO ACCESS TEXT ===")
if hasattr(response, 'text'):
    print(f"✓ Has .text property")
    print(f"  response.text length = {len(response.text)}")
    print(f"  response.text = {repr(response.text[:300])}")
else:
    print(f"✗ NO .text property")

    if hasattr(response, 'candidates'):
        print(f"✓ Has .candidates")
        for i, candidate in enumerate(response.candidates):
            print(f"  Candidate {i}: {candidate}")
            if hasattr(candidate, 'content'):
                print(f"    Has .content: {candidate.content}")
                if hasattr(candidate.content, 'parts'):
                    for j, part in enumerate(candidate.content.parts):
                        print(f"      Part {j}: {part}")  
                        if hasattr(part, 'text'):
                            print(f"        Text (len={len(part.text)}): {repr(part.text[:300])}")

if hasattr(response, 'parts'):
    print(f"✓ Has .parts")
    for i, part in enumerate(response.parts):
        print(f"  Part {i}: {type(part)}")
        if hasattr(part, 'text'):
            print(f"    text (len={len(part.text)}): {repr(part.text[:300])}")

print(f"\n=== STRING REPRESENTATION ===")
str_rep = str(response)
print(f"str(response) length = {len(str_rep)}")
print(f"str(response) = {repr(str_rep[:300])}")
