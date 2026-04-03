import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# List available models
try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error listing models: {str(e)}")
    
# Try to get model info
try:
    model = genai.GenerativeModel('gemini-pro')
    print("\nUsing gemini-pro")
except Exception as e:
    print(f"gemini-pro error: {str(e)}")
