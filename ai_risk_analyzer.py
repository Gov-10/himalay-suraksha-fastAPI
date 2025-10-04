import google.generativeai as genai
import os,re
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_with_gemini(weather_data: dict):
    model = genai.GenerativeModel("gemini-2.5-pro")
    prompt = f"""
    You are a disaster risk assessment AI.
    Given this weather JSON, classify the disaster risk with the following fields:

    {{
      "city": "<city name>",
      "risk_level": "HIGH | MEDIUM | SAFE",
      "hazard_type": "storm | flood | landslide | heatwave | other",
      "reason": "<short explanation (1–2 lines)>"
    }}

    Rules:
    - Respond ONLY in valid JSON (no markdown, no backticks).
    - Choose hazard_type from the given list (storm, flood, landslide, heatwave, other).
    - If no hazard is likely, use "other" with reason "No significant risk".
    - Use risk_level based on severity of the weather data.
    - Be accurate and concise.

    Weather Data: {json.dumps(weather_data)}
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # remove ```json ... ``` if Gemini wraps it
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip("` \n")
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": text}
