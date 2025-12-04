import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv()

from src.backend.pipelines.text.text_evaluator import run_text_evaluation
from src.backend.utils.config import Config

print(f"API Key present: {bool(Config.GEMINI_API_KEY)}")
print(f"Model: {Config.LLM_MODEL}")

transcript = """
Hello my wonderful temp graders, I hope you are doing well and welcome to your summary under 10 minutes session with me. 
As you can see today we will be going over a letter to God from first flight. So without further ado let's get to it. 
So a letter to God is a story written by G.L. Fuentes which depicts the firm faith of a poor and simple minded farmer named Lencho. 
In God. So Lencho was poor yet a very dedicated farmer. He was hoping for a decent harvest. 
But to his dismay or disappointment a hailed storm suddenly came and completely destroyed all of his crops and his harvest.
"""

print("\nRunning evaluation...")
result = run_text_evaluation(transcript)
print("\nResult:")
import json
print(json.dumps(result, indent=2))
