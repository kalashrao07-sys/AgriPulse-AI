from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db.models import CropHealth, Farm, Crop
from app.providers.ai_provider import get_ai_provider
from app.agents import pest_agent
import os

router = APIRouter()
UPLOAD_DIR = "/tmp/agripulse_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze")
async def analyze_crop_image(
    farm_id: Optional[int] = Form(None),
    crop_name: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Analyze uploaded crop image for diseases/pests."""
    provider = get_ai_provider()

    # Determine crop name
    if not crop_name and farm_id:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            crop = db.query(Crop).filter(Crop.farm_id == farm.id, Crop.is_active == True).first()
            if crop:
                crop_name = crop.crop_name

    image_filename = None
    if image and image.filename:
        image_filename = image.filename
        # Save image
        save_path = os.path.join(UPLOAD_DIR, image.filename)
        content = await image.read()
        with open(save_path, "wb") as f:
            f.write(content)

    # Run demo analysis
    analysis = await pest_agent.analyze_image(
        provider=provider,
        crop=crop_name,
        image_filename=image_filename,
    )

    # If symptoms provided, also get text-based advice
    if symptoms:
        text_result = await pest_agent.run(
            provider=provider,
            query=f"I see these symptoms: {symptoms}",
            crop=crop_name,
            symptoms=symptoms,
            image_provided=bool(image_filename),
        )
        analysis["ai_text_response"] = text_result.get("response", "")

    # Save to DB
    crop_id = None
    if farm_id:
        crop = db.query(Crop).filter(Crop.farm_id == farm_id, Crop.is_active == True).first()
        if crop:
            crop_id = crop.id

    health_record = CropHealth(
        crop_id=crop_id,
        image_filename=image_filename,
        analysis_result=analysis,
        disease_detected=analysis.get("disease_detected"),
        confidence_percent=analysis.get("confidence_percent"),
        is_demo_analysis=True,
    )
    db.add(health_record)
    db.commit()

    return analysis


@router.get("/history/{farm_id}")
def get_health_history(farm_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.farm_id == farm_id, Crop.is_active == True).first()
    if not crop:
        return []
    records = (
        db.query(CropHealth)
        .filter(CropHealth.crop_id == crop.id)
        .order_by(CropHealth.created_at.desc())
        .limit(5)
        .all()
    )
    return [
        {
            "id": r.id,
            "disease_detected": r.disease_detected,
            "confidence_percent": r.confidence_percent,
            "is_demo": r.is_demo_analysis,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
