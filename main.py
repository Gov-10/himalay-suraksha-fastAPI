from fastapi import FastAPI, Request, Body
from ai_risk_analyzer import analyze_with_gemini
api = FastAPI(title="Himalay Suraksha - AI Risk Analyzer")
@api.post("/analyze_weather")
async def analyze_weather(weather_data: dict = Body(...)):
    """
    Endpoint called by Orkes Conductor.
    Accepts JSON body directly and analyzes via Gemini.
    """
    result = analyze_with_gemini(weather_data)
    return result
