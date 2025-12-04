import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()

from src.backend.utils.config import Config

api_key = Config.GEMINI_API_KEY
if not api_key:
    print("No API Key found")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
