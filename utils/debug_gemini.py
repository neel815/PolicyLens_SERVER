import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Simple test prompt
prompt = """Return ONLY valid JSON:
{
  "covered_events": ["test1", "test2"],
  "exclusions": ["excl1", "excl2"],
  "risky_clauses": ["risk1"],
  "coverage_score": 7
}"""

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=1,
            max_output_tokens=1024,
            response_mime_type="application/json",
        )
    )
    
    print("Raw Response:")
    print(repr(response.text))
    print("\nFormatted Response:")
    print(response.text)
    
    # Try to parse
    try:
        data = json.loads(response.text)
        print("\n✓ JSON parsed successfully!")
        print(data)
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
