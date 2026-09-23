from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import FarmTimeline, Farm
import datetime

router = APIRouter()


@router.get("/{farm_id}")
def get_timeline(farm_id: int, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")

    events = (
        db.query(FarmTimeline)
        .filter(FarmTimeline.farm_id == farm_id)
        .order_by(FarmTimeline.event_date.asc())
        .all()
    )

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "description": e.event_description,
            "icon": e.event_icon or "📌",
            "date": e.event_date.isoformat(),
            "day_number": e.day_number,
            "is_today": e.event_date == datetime.date.today(),
        }
        for e in events
    ]


@router.post("/{farm_id}/event")
def add_event(
    farm_id: int,
    event_type: str,
    description: str,
    icon: str = "📌",
    db: Session = Depends(get_db),
):
    event = FarmTimeline(
        farm_id=farm_id,
        event_type=event_type,
        event_description=description,
        event_icon=icon,
        event_date=datetime.date.today(),
    )
    db.add(event)
    db.commit()
    return {"success": True, "id": event.id}
