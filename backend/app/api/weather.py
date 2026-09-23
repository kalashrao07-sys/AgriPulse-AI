from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db.models import WeatherRecord, Farm

router = APIRouter()


DEMO_WEATHER = {
    "temperature_celsius": 29.0,
    "humidity_percent": 75.0,
    "rain_probability_percent": 78.0,
    "wind_speed_kmh": 12.0,
    "description": "Partly cloudy with chance of rain",
    "is_demo": True,
}


def _irrigation_recommendation(rain_prob: float, soil_moisture: float) -> dict:
    if rain_prob >= 70 or soil_moisture >= 65:
        return {
            "decision": "DO NOT IRRIGATE TODAY",
            "color": "red",
            "reason": f"Rain probability {rain_prob}% and soil moisture {soil_moisture}% are both high.",
            "icon": "🌧",
        }
    elif soil_moisture <= 35 or rain_prob <= 20:
        return {
            "decision": "IRRIGATE TODAY",
            "color": "blue",
            "reason": f"Soil moisture {soil_moisture}% is low and rain probability {rain_prob}% is low.",
            "icon": "💧",
        }
    else:
        return {
            "decision": "MONITOR SOIL MOISTURE",
            "color": "amber",
            "reason": f"Conditions are borderline. Check soil moisture again tomorrow.",
            "icon": "⚠️",
        }


@router.get("/{farm_id}")
def get_weather(farm_id: int, db: Session = Depends(get_db)):
    """Get weather data for a farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        weather_data = DEMO_WEATHER
        soil_moisture = 64.0
    else:
        weather = (
            db.query(WeatherRecord)
            .filter(WeatherRecord.farm_id == farm_id)
            .order_by(WeatherRecord.recorded_at.desc())
            .first()
        )
        if weather:
            weather_data = {
                "temperature_celsius": float(weather.temperature_celsius or 29.0),
                "humidity_percent": float(weather.humidity_percent or 75.0),
                "rain_probability_percent": float(weather.rain_probability_percent or 78.0),
                "wind_speed_kmh": float(weather.wind_speed_kmh or 12.0),
                "description": "Demo weather conditions",
                "is_demo": weather.is_demo,
            }
        else:
            weather_data = DEMO_WEATHER
        soil_moisture = 64.0  # Default demo value

    irr = _irrigation_recommendation(
        weather_data["rain_probability_percent"],
        soil_moisture,
    )

    return {
        **weather_data,
        "soil_moisture_percent": soil_moisture,
        "irrigation_recommendation": irr,
        "demo_notice": "Demo Weather Data — Live weather API not configured." if weather_data.get("is_demo") else None,
    }


@router.get("/demo/current")
def get_demo_weather():
    """Get demo weather data."""
    irr = _irrigation_recommendation(
        DEMO_WEATHER["rain_probability_percent"],
        64.0,
    )
    return {
        **DEMO_WEATHER,
        "soil_moisture_percent": 64.0,
        "irrigation_recommendation": irr,
        "demo_notice": "Demo Weather Data — Live weather API not configured.",
    }
