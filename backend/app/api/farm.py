from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.db.models import Farm, User, Crop, SoilRecord, WeatherRecord, FarmTimeline
import datetime

router = APIRouter()


class FarmSetupRequest(BaseModel):
    farmer_name: str
    location: str
    size_acres: float
    crop_name: str
    crop_age_days: int
    soil_type: str
    irrigation_method: str


class FarmResponse(BaseModel):
    id: int
    farmer_name: str
    location: str
    size_acres: float
    crop_name: str
    crop_age_days: int
    growth_stage: str
    soil_type: str
    irrigation_method: str
    soil_moisture: float
    temperature: float
    humidity: float
    rain_probability: float
    wind_speed: float
    is_demo_weather: bool


def get_growth_stage(age_days: int, crop: str) -> str:
    crop_lower = crop.lower()
    if crop_lower == "tomato":
        if age_days < 15:
            return "Seedling"
        elif age_days < 30:
            return "Vegetative"
        elif age_days < 60:
            return "Flowering"
        elif age_days < 90:
            return "Fruiting"
        else:
            return "Harvest"
    elif crop_lower in ["wheat", "rice"]:
        if age_days < 30:
            return "Germination"
        elif age_days < 60:
            return "Tillering"
        elif age_days < 90:
            return "Heading"
        else:
            return "Ripening"
    else:
        if age_days < 20:
            return "Seedling"
        elif age_days < 50:
            return "Vegetative"
        elif age_days < 80:
            return "Flowering"
        else:
            return "Harvest"


@router.post("/setup")
def setup_farm(req: FarmSetupRequest, db: Session = Depends(get_db)):
    """Create or update farm profile."""
    # Check if user exists
    user = db.query(User).filter(User.name == req.farmer_name).first()
    if not user:
        user = User(name=req.farmer_name)
        db.add(user)
        db.flush()

    # Check if farm exists
    farm = db.query(Farm).filter(Farm.user_id == user.id).first()
    if farm:
        farm.location = req.location
        farm.size_acres = req.size_acres
        farm.soil_type = req.soil_type
        farm.irrigation_method = req.irrigation_method
    else:
        farm = Farm(
            user_id=user.id,
            name=f"{req.farmer_name}'s Farm",
            location=req.location,
            size_acres=req.size_acres,
            soil_type=req.soil_type,
            irrigation_method=req.irrigation_method,
        )
        db.add(farm)
        db.flush()

    # Update/create crop
    crop = db.query(Crop).filter(Crop.farm_id == farm.id, Crop.is_active == True).first()
    growth_stage = get_growth_stage(req.crop_age_days, req.crop_name)
    if crop:
        crop.crop_name = req.crop_name
        crop.age_days = req.crop_age_days
        crop.growth_stage = growth_stage
    else:
        planted = datetime.date.today() - datetime.timedelta(days=req.crop_age_days)
        crop = Crop(
            farm_id=farm.id,
            crop_name=req.crop_name,
            planted_date=planted,
            age_days=req.crop_age_days,
            growth_stage=growth_stage,
            is_active=True,
        )
        db.add(crop)

    db.commit()
    return {"success": True, "farm_id": farm.id, "user_id": user.id}


@router.get("/demo")
def load_demo_farm(db: Session = Depends(get_db)):
    """Load the demo farm (Ramesh, Belagavi)."""
    user = db.query(User).filter(User.name == "Ramesh").first()
    if not user:
        raise HTTPException(status_code=404, detail="Demo farm not found. Run database initialization.")
    farm = db.query(Farm).filter(Farm.user_id == user.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Demo farm not found.")
    return _build_farm_response(db, user, farm)


@router.get("/{farm_id}")
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")
    user = db.query(User).filter(User.id == farm.user_id).first()
    return _build_farm_response(db, user, farm)


def _build_farm_response(db, user, farm):
    crop = db.query(Crop).filter(Crop.farm_id == farm.id, Crop.is_active == True).first()
    soil = db.query(SoilRecord).filter(SoilRecord.farm_id == farm.id).order_by(SoilRecord.recorded_at.desc()).first()
    weather = db.query(WeatherRecord).filter(WeatherRecord.farm_id == farm.id).order_by(WeatherRecord.recorded_at.desc()).first()

    return {
        "farm_id": farm.id,
        "user_id": user.id if user else None,
        "farmer_name": user.name if user else "Farmer",
        "location": farm.location or "",
        "size_acres": farm.size_acres or 0,
        "soil_type": farm.soil_type or "Loamy",
        "irrigation_method": farm.irrigation_method or "Drip",
        "crop_name": crop.crop_name if crop else "Unknown",
        "crop_age_days": crop.age_days if crop else 0,
        "growth_stage": crop.growth_stage if crop else "Unknown",
        "soil_moisture": soil.moisture_percent if soil else 64.0,
        "soil_ph": soil.ph_level if soil else 6.5,
        "temperature": weather.temperature_celsius if weather else 29.0,
        "humidity": weather.humidity_percent if weather else 75.0,
        "rain_probability": weather.rain_probability_percent if weather else 78.0,
        "wind_speed": weather.wind_speed_kmh if weather else 12.0,
        "is_demo_weather": weather.is_demo if weather else True,
    }
