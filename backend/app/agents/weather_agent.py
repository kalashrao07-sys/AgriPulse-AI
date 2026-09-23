"""
🌦 Weather & Irrigation Agent
Handles: weather info, rain probability, temperature, irrigation recommendations
"""
from typing import Optional
from app.providers.ai_provider import AIProvider

SYSTEM_PROMPT = """You are an expert agricultural meteorologist and irrigation specialist for Indian farming.
Provide clear, concise irrigation and weather-based recommendations. Be direct with yes/no irrigation decisions.
Focus on practical advice based on the given weather and soil data."""


async def run(
    provider: AIProvider,
    query: str,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    rain_probability: Optional[float] = None,
    soil_moisture: Optional[float] = None,
    wind_speed: Optional[float] = None,
    crop: Optional[str] = None,
    irrigation_method: Optional[str] = None,
) -> dict:
    """Run the Weather & Irrigation Agent."""

    # Build weather context
    weather_parts = []
    if temperature is not None:
        weather_parts.append(f"Temperature: {temperature}°C")
    if humidity is not None:
        weather_parts.append(f"Humidity: {humidity}%")
    if rain_probability is not None:
        weather_parts.append(f"Rain probability: {rain_probability}%")
    if soil_moisture is not None:
        weather_parts.append(f"Soil moisture: {soil_moisture}%")
    if wind_speed is not None:
        weather_parts.append(f"Wind speed: {wind_speed} km/h")
    if crop:
        weather_parts.append(f"Crop: {crop}")
    if irrigation_method:
        weather_parts.append(f"Irrigation method: {irrigation_method}")

    weather_info = "\n".join(weather_parts)

    # Determine irrigation recommendation based on data
    irrigation_recommendation = _get_irrigation_recommendation(rain_probability, soil_moisture)

    prompt = f"""Current Weather & Soil Data:
{weather_info}

Farmer's Question: {query}

Based on this data, provide:
1. Clear irrigation decision (irrigate / delay / reduce)
2. Weather risk assessment
3. Specific recommendation for today

Keep response under 150 words. Be direct and specific."""

    try:
        result = await provider.generate(prompt, SYSTEM_PROMPT)
        return {
            "agent": "Weather & Irrigation Agent",
            "success": True,
            "response": result,
            "irrigation_recommendation": irrigation_recommendation,
            "weather_data": {
                "temperature": temperature,
                "humidity": humidity,
                "rain_probability": rain_probability,
                "soil_moisture": soil_moisture,
            },
        }
    except Exception as e:
        return {
            "agent": "Weather & Irrigation Agent",
            "success": False,
            "response": _fallback_response(rain_probability, soil_moisture, crop),
            "irrigation_recommendation": irrigation_recommendation,
            "weather_data": {
                "temperature": temperature,
                "humidity": humidity,
                "rain_probability": rain_probability,
                "soil_moisture": soil_moisture,
            },
            "error": str(e),
        }


def _get_irrigation_recommendation(rain_prob: Optional[float], soil_moisture: Optional[float]) -> str:
    if rain_prob is not None and rain_prob >= 70:
        return "DELAY"
    if soil_moisture is not None and soil_moisture >= 60:
        return "DELAY"
    if soil_moisture is not None and soil_moisture <= 30:
        return "IRRIGATE"
    if rain_prob is not None and rain_prob <= 20:
        return "IRRIGATE"
    return "MONITOR"


def _fallback_response(rain_prob, soil_moisture, crop) -> str:
    rec = _get_irrigation_recommendation(rain_prob, soil_moisture)
    crop_name = crop or "your crop"
    if rec == "DELAY":
        return (
            f"Based on {rain_prob}% rain probability and {soil_moisture}% soil moisture, "
            f"it is recommended to DELAY irrigation for {crop_name} today. "
            f"Rain is expected and soil moisture is adequate."
        )
    elif rec == "IRRIGATE":
        return (
            f"Soil moisture at {soil_moisture}% is low. Proceed with irrigation for {crop_name}. "
            f"Use drip irrigation for efficient water use."
        )
    return f"Monitor soil moisture closely for {crop_name}. Irrigate if moisture drops below 40%."
