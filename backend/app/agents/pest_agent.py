"""
🐛 Pest & Disease Agent
Handles: crop diseases, pest identification, image analysis (demo mode)
"""
from typing import Optional
from app.providers.ai_provider import AIProvider

SYSTEM_PROMPT = """You are an expert plant pathologist and pest management specialist for Indian agriculture.
Identify diseases and pests from descriptions, provide treatment recommendations using organic and chemical options.
Always recommend consulting a local agricultural officer for serious infestations."""


async def run(
    provider: AIProvider,
    query: str,
    crop: Optional[str] = None,
    symptoms: Optional[str] = None,
    image_provided: bool = False,
) -> dict:
    """Run the Pest & Disease Agent."""

    context_parts = []
    if crop:
        context_parts.append(f"Crop: {crop}")
    if symptoms:
        context_parts.append(f"Observed symptoms: {symptoms}")
    if image_provided:
        context_parts.append("(Image uploaded for analysis)")

    context = "\n".join(context_parts) if context_parts else "No additional context"

    prompt = f"""Crop Information:
{context}

Farmer's Question: {query}

Provide:
1. Possible disease or pest identification
2. Severity assessment (Low/Medium/High)
3. Treatment recommendation (organic + chemical options)
4. Prevention steps

Keep response under 200 words."""

    try:
        result = await provider.generate(prompt, SYSTEM_PROMPT)
        return {
            "agent": "Pest & Disease Agent",
            "success": True,
            "response": result,
            "image_analysis": None,
        }
    except Exception as e:
        return {
            "agent": "Pest & Disease Agent",
            "success": False,
            "response": _fallback_response(crop, query),
            "image_analysis": None,
            "error": str(e),
        }


async def analyze_image(
    provider: AIProvider,
    crop: Optional[str] = None,
    image_filename: Optional[str] = None,
) -> dict:
    """
    Demo crop image analysis.
    NOTE: This is DEMO ANALYSIS — not produced by a real vision model.
    A real vision model (e.g., LLaVA or GPT-4V) would be needed for accurate results.
    """
    crop_name = crop or "Tomato"

    # Demo analysis results for common tomato diseases
    demo_results = [
        {
            "disease": "Early Blight (Alternaria solani)",
            "confidence": 72.4,
            "severity": "Medium",
            "symptoms": "Brown spots with concentric rings on lower leaves",
            "treatment": "Apply Mancozeb 75 WP @ 2g/L or Copper oxychloride. Remove infected leaves.",
            "prevention": "Avoid overhead irrigation. Maintain plant spacing. Rotate crops.",
        },
        {
            "disease": "Leaf Miner",
            "confidence": 65.8,
            "severity": "Low",
            "symptoms": "Serpentine mines/tunnels visible on leaves",
            "treatment": "Apply Spinosad or Abamectin. Yellow sticky traps for monitoring.",
            "prevention": "Regular scouting. Destroy infested leaves. Use reflective mulch.",
        },
        {
            "disease": "No Disease Detected",
            "confidence": 81.2,
            "severity": "None",
            "symptoms": "Leaves appear healthy",
            "treatment": "Continue regular monitoring and preventive spray schedule.",
            "prevention": "Maintain balanced fertilization. Ensure proper drainage.",
        },
    ]

    import random
    result = random.choice(demo_results)

    return {
        "agent": "Pest & Disease Agent",
        "is_demo": True,
        "demo_notice": "⚠️ DEMO ANALYSIS — Not produced by a real vision model. For accurate diagnosis, use a trained plant disease model.",
        "crop": crop_name,
        "image_filename": image_filename,
        "disease_detected": result["disease"],
        "confidence_percent": result["confidence"],
        "severity": result["severity"],
        "symptoms": result["symptoms"],
        "treatment": result["treatment"],
        "prevention": result["prevention"],
    }


def _fallback_response(crop, query) -> str:
    crop_name = crop or "your crop"
    return (
        f"For {crop_name}: Common issues include fungal diseases (early blight, late blight), "
        f"bacterial infections, and pest infestations like aphids and mites. "
        f"Scout regularly, remove infected plant material, and apply appropriate fungicide/pesticide. "
        f"Consult your local Krishi Vigyan Kendra for precise diagnosis."
    )
