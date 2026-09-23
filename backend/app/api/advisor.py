from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.database import get_db
from app.db.models import AIRecommendation, AgentRun, Farm, Crop, SoilRecord, WeatherRecord
from app.providers.ai_provider import get_ai_provider
from app.agents import supervisor
import time

router = APIRouter()


class AdvisoryRequest(BaseModel):
    query: str
    farm_id: Optional[int] = None


class AdvisoryResponse(BaseModel):
    query: str
    recommendation: str
    agents_used: List[str]
    sources: List[str]
    confidence: str
    provider: str


@router.post("/ask", response_model=AdvisoryResponse)
async def ask_advisor(req: AdvisoryRequest, db: Session = Depends(get_db)):
    """Main AI advisor endpoint — routes to supervisor."""
    provider = get_ai_provider()

    # Load farm context
    farm_data = {}
    if req.farm_id:
        farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
        if farm:
            crop = db.query(Crop).filter(Crop.farm_id == farm.id, Crop.is_active == True).first()
            soil = db.query(SoilRecord).filter(SoilRecord.farm_id == farm.id).order_by(SoilRecord.recorded_at.desc()).first()
            weather = db.query(WeatherRecord).filter(WeatherRecord.farm_id == farm.id).order_by(WeatherRecord.recorded_at.desc()).first()
            user = farm.user

            farm_data = {
                "farmer_name": user.name if user else "Farmer",
                "location": farm.location or "",
                "soil_type": farm.soil_type or "Loamy",
                "irrigation_method": farm.irrigation_method or "Drip",
                "crop_name": crop.crop_name if crop else "Tomato",
                "crop_age_days": crop.age_days if crop else 45,
                "growth_stage": crop.growth_stage if crop else "Flowering",
                "soil_moisture": float(soil.moisture_percent) if soil else 64.0,
                "temperature": float(weather.temperature_celsius) if weather else 29.0,
                "humidity": float(weather.humidity_percent) if weather else 75.0,
                "rain_probability": float(weather.rain_probability_percent) if weather else 78.0,
                "wind_speed": float(weather.wind_speed_kmh) if weather else 12.0,
            }
    else:
        # Default demo farm context
        farm_data = {
            "farmer_name": "Farmer",
            "crop_name": "Tomato",
            "crop_age_days": 45,
            "growth_stage": "Flowering",
            "soil_type": "Loamy",
            "irrigation_method": "Drip",
            "soil_moisture": 64.0,
            "temperature": 29.0,
            "humidity": 75.0,
            "rain_probability": 78.0,
            "wind_speed": 12.0,
        }

    start = time.time()
    result = await supervisor.run(
        provider=provider,
        query=req.query,
        db=db,
        farm_data=farm_data,
    )
    duration_ms = int((time.time() - start) * 1000)

    # Save recommendation
    if req.farm_id:
        rec = AIRecommendation(
            farm_id=req.farm_id,
            user_query=req.query,
            recommendation=result["recommendation"],
            agents_used=result["agent_names_raw"],
            sources=result["sources"],
            confidence=result["confidence"],
        )
        db.add(rec)

        # Log agent run
        run_log = AgentRun(
            farm_id=req.farm_id,
            query=req.query,
            agent_name="supervisor",
            result={"agents": result["agent_names_raw"]},
            duration_ms=duration_ms,
        )
        db.add(run_log)
        db.commit()

    return AdvisoryResponse(
        query=req.query,
        recommendation=result["recommendation"],
        agents_used=result["agents_used"],
        sources=result["sources"],
        confidence=result["confidence"],
        provider=provider.provider_name,
    )


@router.get("/history/{farm_id}")
def get_history(farm_id: int, db: Session = Depends(get_db)):
    recs = (
        db.query(AIRecommendation)
        .filter(AIRecommendation.farm_id == farm_id)
        .order_by(AIRecommendation.created_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": r.id,
            "query": r.user_query,
            "recommendation": r.recommendation,
            "agents_used": r.agents_used,
            "sources": r.sources,
            "confidence": r.confidence,
            "created_at": r.created_at.isoformat(),
        }
        for r in recs
    ]
