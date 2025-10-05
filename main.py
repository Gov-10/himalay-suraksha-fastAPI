from fastapi import FastAPI, Body
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
async def analyze_weather(weather_data: dict = Body(...)):
    """
    Endpoint called by Orkes Conductor.
    Accepts possibly stringified JSON and auto-converts to floats before validation.
    """

    # --- Safe type coercion for Orkes string inputs ---
    numeric_fields = ["temperature", "rainfall_24h", "humidity", "windspeed"]
    for field in numeric_fields:
        if field in weather_data and isinstance(weather_data[field], str):
            try:
                weather_data[field] = float(weather_data[field])
            except ValueError:
                weather_data[field] = 0.0  # fallback if invalid

    # --- Validate after coercion ---
    validated_data = WeatherData(**weather_data)

    # --- Analyze with Gemini ---
    result = analyze_with_gemini(validated_data.dict())
    return result
