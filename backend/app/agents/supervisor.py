"""
🤖 Farm Supervisor Agent
Routes farmer queries to appropriate specialized agents and synthesizes results
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.providers.ai_provider import AIProvider
from app.agents import crop_agent, weather_agent, pest_agent, rag_agent

SYSTEM_PROMPT = """You are AgriPulse, an intelligent farm advisor for Indian farmers.
Synthesize information from multiple specialist agents into one clear, actionable recommendation.
Be concise, practical, and empathetic to the farmer's situation.
Structure your response with: Main Recommendation, Why, and Action Steps.
Do not expose internal agent reasoning. Present only the final synthesized advice."""

# Query routing keywords
WEATHER_KEYWORDS = ["irrigat", "water", "rain", "weather", "temperature", "humid", "drought", "flood", "moisture"]
CROP_KEYWORDS = ["fertiliz", "nutrient", "harvest", "plant", "growth", "yield", "crop", "sow", "germinate", "flower", "fruit"]
PEST_KEYWORDS = ["disease", "pest", "insect", "fungus", "blight", "rot", "wilt", "spot", "yellowing", "dying", "sick", "leaf", "damage"]


def route_query(query: str) -> List[str]:
    """Determine which agents to invoke based on query content."""
    query_lower = query.lower()
    agents = []

    if any(kw in query_lower for kw in WEATHER_KEYWORDS):
        agents.append("weather")
    if any(kw in query_lower for kw in CROP_KEYWORDS):
        agents.append("crop")
    if any(kw in query_lower for kw in PEST_KEYWORDS):
        agents.append("pest")

    # RAG always included for knowledge grounding
    agents.append("rag")

    # Default: if no specific agent matched, include all
    if len(agents) == 1:  # only RAG
        agents = ["crop", "weather", "rag"]

    return list(dict.fromkeys(agents))  # deduplicate preserving order


async def run(
    provider: AIProvider,
    query: str,
    db: Session,
    farm_data: Optional[dict] = None,
) -> dict:
    """
    Farm Supervisor: Routes query, runs agents, synthesizes recommendation.
    """
    farm_data = farm_data or {}
    agent_names = route_query(query)

    agent_results = {}
    sources = []

    # Run selected agents
    if "crop" in agent_names:
        result = await crop_agent.run(
            provider=provider,
            query=query,
            crop=farm_data.get("crop_name"),
            crop_age_days=farm_data.get("crop_age_days"),
            growth_stage=farm_data.get("growth_stage"),
            soil_type=farm_data.get("soil_type"),
        )
        agent_results["crop"] = result

    if "weather" in agent_names:
        result = await weather_agent.run(
            provider=provider,
            query=query,
            temperature=farm_data.get("temperature"),
            humidity=farm_data.get("humidity"),
            rain_probability=farm_data.get("rain_probability"),
            soil_moisture=farm_data.get("soil_moisture"),
            wind_speed=farm_data.get("wind_speed"),
            crop=farm_data.get("crop_name"),
            irrigation_method=farm_data.get("irrigation_method"),
        )
        agent_results["weather"] = result

    if "pest" in agent_names:
        result = await pest_agent.run(
            provider=provider,
            query=query,
            crop=farm_data.get("crop_name"),
        )
        agent_results["pest"] = result

    if "rag" in agent_names:
        result = await rag_agent.run(
            provider=provider,
            query=query,
            db=db,
            crop=farm_data.get("crop_name"),
        )
        agent_results["rag"] = result
        if result.get("sources"):
            sources.extend(result["sources"])

    # Synthesize final recommendation
    synthesis = await _synthesize(provider, query, agent_results, farm_data)

    # Build display agent names
    display_agents = []
    agent_display_map = {
        "crop": "🌱 Crop Advisory Agent",
        "weather": "🌦 Weather & Irrigation Agent",
        "pest": "🐛 Pest & Disease Agent",
        "rag": "📚 Agricultural RAG Agent",
    }
    for a in agent_names:
        display_agents.append(agent_display_map.get(a, a))

    return {
        "query": query,
        "recommendation": synthesis,
        "agents_used": display_agents,
        "agent_names_raw": agent_names,
        "sources": list(set(sources)) if sources else ["Agricultural Knowledge Base"],
        "confidence": _determine_confidence(agent_results),
        "agent_details": agent_results,
        "farm_context": farm_data,
    }


async def _synthesize(
    provider: AIProvider,
    query: str,
    agent_results: dict,
    farm_data: dict,
) -> str:
    """Synthesize agent outputs into one coherent recommendation."""

    agent_summaries = []
    for agent_key, result in agent_results.items():
        if result.get("success") and result.get("response"):
            label = result.get("agent", agent_key)
            agent_summaries.append(f"[{label}]\n{result['response']}")

    if not agent_summaries:
        return _build_rule_based_recommendation(query, farm_data, agent_results)

    combined = "\n\n".join(agent_summaries)
    farmer_name = farm_data.get("farmer_name", "Farmer")
    crop = farm_data.get("crop_name", "your crop")
    location = farm_data.get("location", "")

    prompt = f"""You have received input from specialized farming agents. Synthesize these into ONE clear recommendation for the farmer.

Agent Inputs:
{combined}

Farmer: {farmer_name}
Crop: {crop}
Location: {location}
Question: {query}

Write a focused farm recommendation (150-200 words) with:
1. MAIN RECOMMENDATION (bold/clear decision)
2. WHY (key factors: 2-3 bullet points)
3. ACTION STEPS (what to do today/this week)

Do NOT repeat all agent details. Give ONE unified, actionable answer."""

    try:
        return await provider.generate(prompt, SYSTEM_PROMPT)
    except Exception:
        return _build_rule_based_recommendation(query, farm_data, agent_results)


def _build_rule_based_recommendation(query: str, farm_data: dict, agent_results: dict) -> str:
    """Rule-based fallback recommendation when AI is unavailable."""
    crop = farm_data.get("crop_name", "your crop")
    rain_prob = farm_data.get("rain_probability", 0)
    soil_moisture = farm_data.get("soil_moisture", 50)
    crop_age = farm_data.get("crop_age_days", 0)
    stage = farm_data.get("growth_stage", "")

    query_lower = query.lower()

    if any(w in query_lower for w in ["irrigat", "water"]):
        if rain_prob >= 70 or soil_moisture >= 60:
            return (
                f"**Delay irrigation for {crop} today.**\n\n"
                f"• Rain probability is {rain_prob}% — rainfall expected\n"
                f"• Soil moisture at {soil_moisture}% is adequate\n"
                f"• {crop} at {crop_age} days ({stage}) does not require additional water now\n\n"
                f"**Action:** Check again in 2 days. If rain doesn't arrive and moisture drops below 40%, irrigate immediately."
            )
        else:
            return (
                f"**Proceed with irrigation for {crop}.**\n\n"
                f"• Soil moisture at {soil_moisture}% is below optimal\n"
                f"• Rain probability is only {rain_prob}%\n\n"
                f"**Action:** Apply 20-25mm water using drip irrigation in the morning."
            )

    if any(w in query_lower for w in ["fertiliz", "nutrient"]):
        return (
            f"**Apply balanced fertilizer to {crop} at {crop_age} days.**\n\n"
            f"• {crop} at {stage} stage needs adequate NPK nutrition\n"
            f"• Avoid over-fertilization which can cause leaf burn\n\n"
            f"**Action:** Apply 19:19:19 NPK @ 5g/L via drip or foliar spray. Test soil pH first."
        )

    return (
        f"**Farm Advisory for {crop} ({crop_age} days):**\n\n"
        f"• Monitor crop daily for stress signs\n"
        f"• Current weather: {rain_prob}% rain probability, soil moisture {soil_moisture}%\n"
        f"• Growth stage: {stage}\n\n"
        f"**Action:** Follow standard {crop} cultivation practices for {stage} stage."
    )


def _determine_confidence(agent_results: dict) -> str:
    successful = sum(1 for r in agent_results.values() if r.get("success", False))
    total = len(agent_results)
    if total == 0:
        return "Low"
    ratio = successful / total
    if ratio >= 0.8:
        return "High"
    elif ratio >= 0.5:
        return "Medium"
    return "Low"
