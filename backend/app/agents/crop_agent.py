"""
🌱 Crop Advisory Agent
Handles: crop advice, growth stages, fertilizer, harvesting
"""
from typing import Optional
from app.providers.ai_provider import AIProvider

SYSTEM_PROMPT = """You are an expert agricultural crop advisor with deep knowledge of Indian farming.
You provide concise, practical advice about crop management, fertilizers, growth stages, and harvesting.
Keep responses focused and actionable. Use metric units. Be specific to Indian farming conditions."""


async def run(
    provider: AIProvider,
    query: str,
    crop: Optional[str] = None,
    crop_age_days: Optional[int] = None,
    growth_stage: Optional[str] = None,
    soil_type: Optional[str] = None,
    farm_context: Optional[str] = None,
) -> dict:
    """Run the Crop Advisory Agent."""

    context_parts = []
    if crop:
        context_parts.append(f"Crop: {crop}")
    if crop_age_days is not None:
        context_parts.append(f"Crop age: {crop_age_days} days")
    if growth_stage:
        context_parts.append(f"Growth stage: {growth_stage}")
    if soil_type:
        context_parts.append(f"Soil type: {soil_type}")
    if farm_context:
        context_parts.append(f"Additional context: {farm_context}")

    farm_info = "\n".join(context_parts)

    prompt = f"""Farm Information:
{farm_info}

Farmer's Question: {query}

Provide a focused crop advisory response covering:
1. Direct answer/recommendation
2. Key factors considered
3. Specific action steps

Keep the response practical and within 200 words."""

    try:
        result = await provider.generate(prompt, SYSTEM_PROMPT)
        return {
            "agent": "Crop Advisory Agent",
            "success": True,
            "response": result,
            "factors": extract_factors(crop, crop_age_days, growth_stage),
        }
    except Exception as e:
        return {
            "agent": "Crop Advisory Agent",
            "success": False,
            "response": get_fallback_response(query, crop, crop_age_days, growth_stage),
            "factors": extract_factors(crop, crop_age_days, growth_stage),
            "error": str(e),
        }


def extract_factors(crop, age, stage) -> list:
    factors = []
    if crop:
        factors.append(f"Crop: {crop}")
    if age is not None:
        factors.append(f"Age: {age} days")
    if stage:
        factors.append(f"Stage: {stage}")
    return factors


def get_fallback_response(query, crop, age, stage) -> str:
    crop_name = crop or "your crop"
    stage_info = f" at {stage} stage" if stage else ""
    age_info = f" ({age} days old)" if age else ""
    return (
        f"For {crop_name}{age_info}{stage_info}: Ensure adequate nutrition and monitor for stress signs. "
        f"For fertilizers at this stage, apply balanced NPK based on soil test. "
        f"Maintain proper irrigation schedule and scout regularly for pests."
    )
