import google.generativeai as genai
import os, re, json
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Post-processing safety net ---
def post_process_risks(weather_data, ai_output):
    risks = ai_output.get("risks", [])
    rainfall = weather_data.get("rainfall_24h", 0)
    snow_depth = weather_data.get("snow_depth", 0)
    temp = weather_data.get("temperature", 15)
    windspeed = weather_data.get("windspeed", 0)

    enforced = []

    # --- Hard thresholds for Himalayas ---
    if rainfall > 100:
        enforced.append({
            "hazard_type": "landslide",
            "risk_level": "HIGH" if rainfall > 150 else "MEDIUM",
            "reason": f"Rainfall {rainfall}mm exceeds landslide threshold."
        })
    if rainfall > 150:
        enforced.append({
            "hazard_type": "flood",
            "risk_level": "MEDIUM" if rainfall < 200 else "HIGH",
            "reason": f"Rainfall {rainfall}mm indicates potential flooding."
        })
    if snow_depth > 50 and temp > 5:
        enforced.append({
            "hazard_type": "avalanche",
            "risk_level": "MEDIUM",
            "reason": f"Snow depth {snow_depth}cm with temp {temp}°C increases avalanche risk."
        })
    if windspeed > 80:
        enforced.append({
            "hazard_type": "storm",
            "risk_level": "MEDIUM" if windspeed < 120 else "HIGH",
            "reason": f"Windspeed {windspeed} km/h is dangerous."
        })

    # Merge enforced rules with AI risks (avoid duplicates)
    existing_types = {r["hazard_type"] for r in risks}
    for e in enforced:
        if e["hazard_type"] not in existing_types:
            risks.append(e)

    ai_output["risks"] = risks
    return ai_output


# --- Main AI Analysis ---
def analyze_with_gemini(weather_data: dict):
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    You are a disaster risk analysis system for the Himalayan region.
    Analyze the following weather data and classify risks for multiple hazards.

    Weather Data: {json.dumps(weather_data)}

    Respond ONLY in strict JSON with this schema:

    {{
      "city": "<city name>",
      "risks": [
        {{
          "hazard_type": "flood | landslide | storm | heatwave | avalanche | cloudburst | other",
          "risk_level": "LOW | MEDIUM | HIGH",
          "reason": "<short reasoning, 1-2 lines>"
        }}
      ]
    }}

    Rules:
    - Hazards must be chosen realistically based on Himalayan conditions:
      - landslides → heavy rainfall + steep slopes
      - floods → continuous rain + rising river discharge
      - avalanches → snow + sudden warming
      - cloudbursts → extreme rainfall in short duration
      - storms → high windspeed + rainfall
    - If no hazard is likely, return only one entry:
      {{ "hazard_type": "other", "risk_level": "LOW", "reason": "No significant risk" }}
    - Do NOT output markdown or backticks, just valid JSON.
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean Gemini's response if it adds formatting
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip("` \n")

    try:
        parsed = json.loads(text)
        return post_process_risks(weather_data, parsed)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": text}
