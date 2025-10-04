import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# List all models available to your API key
for model in genai.list_models():
    print(f"Name: {model.name}")
    print(f"Supports: {model.supported_generation_methods}")
    print("-" * 40)
