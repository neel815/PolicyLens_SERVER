import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# Simple prompt to get JSON response
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

try:
    response = model.generate_content(
        prompt,
        request_options={"timeout": 45}
    )
    
    print("=== RAW RESPONSE ===")
    print(repr(response.text))
    print("\n=== RESPONSE LENGTH ===")
    print(f"Length: {len(response.text)}")
    print("\n=== RESPONSE WITH VISIBLE CHARS ===")
    print(response.text)
    print("\n=== FIRST 500 CHARS (repr) ===")
    print(repr(response.text[:500]))
    print("\n=== CHECKING FOR MARKDOWN ===")
    print(f"Starts with backticks: {response.text.startswith('```')}")
    print(f"Contains '```json': {'```json' in response.text}")
    print(f"Contains '```': {'```' in response.text}")
    
    # Try to find JSON bounds
    first_brace = response.text.find('{')
    last_brace = response.text.rfind('}')
    print(f"\n=== JSON BOUNDS ===")
    print(f"First {{ at position: {first_brace}")
    print(f"Last }} at position: {last_brace}")
    
    if first_brace != -1 and last_brace != -1:
        potential_json = response.text[first_brace:last_brace+1]
        print(f"\n=== POTENTIAL JSON ===")
        print(repr(potential_json[:200]))
        print("\n=== TRYING TO PARSE ===")
        try:
            parsed = json.loads(potential_json)
            print("✓ SUCCESS! Parsed JSON:")
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError as e:
            print(f"✗ FAILED: {e}")
            print(f"Extracting substring: {repr(potential_json[:100])}")
    
except Exception as e:
    print(f"Error: {e}")
