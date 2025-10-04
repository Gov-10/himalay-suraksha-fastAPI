from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from ai_risk_analyzer import analyze_with_gemini

# ------------------ SCHEMAS ------------------

class WeatherData(BaseModel):
    city: str
    temperature: float
    rainfall_24h: float
    humidity: float
    windspeed: float
    elevation: Optional[str] = None
    terrain: Optional[str] = None

class Risk(BaseModel):
    hazard_type: str
    risk_level: str
    reason: str

class RiskAnalysisResponse(BaseModel):
    city: str
    risks: List[Risk]

# ------------------ FASTAPI APP ------------------

api = FastAPI(title="Himalay Suraksha - AI Risk Analyzer")

@api.post("/analyze_weather", response_model=RiskAnalysisResponse)
async def analyze_weather(weather_data: WeatherData):
    """
    Endpoint called by Orkes Conductor.
    Accepts validated weather data and analyzes via Gemini.
    """
    result = analyze_with_gemini(weather_data.dict())
    return result
