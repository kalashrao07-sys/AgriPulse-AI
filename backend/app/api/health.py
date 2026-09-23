from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.providers.ai_provider import get_ai_provider
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """System health check."""
    provider = get_ai_provider()
    ai_available = await provider.is_available()

    # Check DB
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    # Check RAG
    try:
        from app.db.models import KnowledgeChunk
        chunk_count = db.query(KnowledgeChunk).count()
        rag_ready = chunk_count > 0
    except Exception:
        rag_ready = False
        chunk_count = 0

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "ai_provider": provider.provider_name,
        "ai_available": ai_available,
        "rag_chunks": chunk_count,
        "rag_ready": rag_ready,
        "agents": {
            "crop_agent": "ready",
            "weather_agent": "ready",
            "pest_agent": "ready",
            "rag_agent": "ready" if rag_ready else "no_data",
        },
        "config": {
            "ai_provider": settings.AI_PROVIDER,
            "ollama_model": settings.OLLAMA_MODEL,
        },
    }
