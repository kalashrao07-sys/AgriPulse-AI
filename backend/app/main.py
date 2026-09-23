"""
AgriPulse AI — FastAPI Backend
Smart Advice. Better Farming.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import farm, advisor, crop_health, weather, timeline, health
from app.db.database import engine
from app.db import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AgriPulse AI",
    description="AI-powered farming advisory system using Ollama/Llama locally and IBM watsonx.ai/Granite for production.",
    version="1.0.0",
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(farm.router, prefix="/api/farm", tags=["Farm"])
app.include_router(advisor.router, prefix="/api/advisor", tags=["AI Advisor"])
app.include_router(crop_health.router, prefix="/api/crop-health", tags=["Crop Health"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(timeline.router, prefix="/api/timeline", tags=["Timeline"])
app.include_router(health.router, prefix="/api", tags=["System"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed knowledge base on startup."""
    logger.info("🌱 AgriPulse AI starting up...")

    # Create tables if not exists
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ DB init error: {e}")

    # Seed knowledge base
    try:
        await seed_knowledge_base()
        logger.info("✅ Knowledge base ready")
    except Exception as e:
        logger.warning(f"⚠️  Knowledge base seeding skipped: {e}")

    logger.info("🚀 AgriPulse AI is ready!")


async def seed_knowledge_base():
    """Load agricultural knowledge documents into RAG pipeline."""
    from app.db.database import SessionLocal
    from app.rag.pipeline import ingest_document
    from app.db.models import KnowledgeChunk
    import os

    db = SessionLocal()
    try:
        # Check if already seeded
        count = db.query(KnowledgeChunk).count()
        if count > 0:
            logger.info(f"📚 Knowledge base already has {count} chunks")
            return

        # Load knowledge files
        kb_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
        kb_dir = os.path.normpath(kb_dir)

        if os.path.exists(kb_dir):
            for filename in os.listdir(kb_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(kb_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    title = filename.replace(".txt", "").replace("_", " ").title()
                    category = _get_category(filename)
                    doc = ingest_document(db, title, category, content)
                    logger.info(f"📖 Ingested: {title}")
        else:
            # Inline fallback knowledge
            _seed_inline_knowledge(db)

    finally:
        db.close()


def _get_category(filename: str) -> str:
    fname = filename.lower()
    if "tomato" in fname:
        return "Crop Management"
    if "rice" in fname or "wheat" in fname:
        return "Crop Management"
    if "irrigat" in fname:
        return "Irrigation"
    if "fertiliz" in fname or "nutrient" in fname:
        return "Fertilization"
    if "disease" in fname or "pest" in fname:
        return "Pest & Disease"
    return "General Agriculture"


def _seed_inline_knowledge(db):
    from app.rag.pipeline import ingest_document

    docs = [
        (
            "Tomato Cultivation Guide",
            "Crop Management",
            """Tomato (Solanum lycopersicum) is a warm-season crop widely grown in Karnataka and across India.
Optimal temperature range is 20-27°C. Tomatoes require well-drained loamy soil with pH 6.0-7.0.
Growth stages: Seedling (0-15 days), Vegetative (15-30 days), Flowering (30-60 days), Fruiting (60-90 days), Harvest (90-120 days).
Spacing: 60cm x 45cm for determinate varieties. Stake plants at 30-35 days.
Fertilizer schedule: At planting apply FYM 25t/ha + DAP 250kg/ha. At 30 days: Urea 50kg/ha. At flowering: MOP 50kg/ha.
Irrigation: Drip irrigation is most efficient. Apply 35-40mm water per week during flowering. Reduce during fruiting.
Common varieties in Karnataka: Arka Vikas, Arka Rakshak, NS 585, Rashmi.""",
        ),
        (
            "Irrigation Management Guide",
            "Irrigation",
            """Efficient irrigation is critical for crop success. Soil moisture should be maintained at 50-70% field capacity.
Drip irrigation reduces water use by 40-50% compared to flood irrigation.
Signs of water stress: wilting in morning, leaf curling, yellowing of lower leaves.
Over-irrigation signs: yellowing, root rot, fungal disease.
Irrigation scheduling: Use soil moisture sensors or the feel method. Sandy soils need more frequent irrigation.
When to delay irrigation: Rain probability above 60%, soil moisture above 65%, waterlogged conditions.
When to irrigate: Soil moisture below 40%, more than 7 days since last rain, crop showing stress.
Drip system maintenance: Check emitter flow weekly. Flush laterals monthly. Monitor pressure.
Water requirement by stage (Tomato): Seedling 15mm/week, Vegetative 25mm/week, Flowering 35-40mm/week, Fruiting 30mm/week.""",
        ),
        (
            "Fertilizer and Nutrient Management",
            "Fertilization",
            """Soil testing is the foundation of fertilizer management. Test soil before every season.
NPK requirements for tomato: 120:60:60 kg/ha (Nitrogen:Phosphorus:Potassium).
Nitrogen (N): Promotes vegetative growth. Deficiency causes yellowing of older leaves. Apply Urea or DAP.
Phosphorus (P): Essential for root development and flowering. Deficiency causes purple leaf color. Apply SSP or DAP.
Potassium (K): Improves fruit quality and disease resistance. Deficiency causes leaf margin browning. Apply MOP.
Secondary nutrients: Calcium prevents blossom end rot in tomato. Magnesium prevents interveinal chlorosis.
Organic matter: Apply FYM (Farm Yard Manure) 20-25 tonnes/ha or compost before planting.
Foliar nutrition: Apply 19:19:19 NPK @ 5g/L water at flowering and fruiting stages.
Split application: Apply 30% N at planting, 30% at 30 days, 40% at flowering for better uptake.""",
        ),
        (
            "Common Crop Diseases and Management",
            "Pest & Disease",
            """Early Blight (Alternaria solani): Brown spots with concentric rings on lower leaves. Spreads upward.
Control: Mancozeb 75WP @ 2g/L or Copper oxychloride @ 3g/L. Remove infected leaves. Avoid overhead irrigation.
Late Blight (Phytophthora infestans): Water-soaked lesions, white sporulation on leaf undersides. Very destructive.
Control: Metalaxyl + Mancozeb @ 2.5g/L. Apply preventively in humid weather.
Bacterial Wilt: Sudden wilting without yellowing. Cut stem shows brown vascular tissue.
Control: No effective chemical. Use resistant varieties. Soil solarization. Crop rotation.
Leaf Miner: Serpentine mines on leaves. Larvae feed inside leaf tissue.
Control: Spinosad @ 0.2ml/L or Abamectin @ 0.5ml/L. Yellow sticky traps for monitoring.
Aphids: Small green/black insects on shoot tips. Secrete honeydew causing sooty mold.
Control: Imidacloprid @ 0.3ml/L or neem oil @ 3ml/L. Use reflective mulch.
Integrated Pest Management: Scout weekly. Use pheromone traps. Encourage beneficial insects. Spray only when threshold exceeded.""",
        ),
        (
            "Rice Cultivation Guide",
            "Crop Management",
            """Rice (Oryza sativa) is the staple food crop of Karnataka. Main seasons: Kharif (June-November), Rabi (November-April).
Water requirement: 1200-1400mm per season. Maintain 5cm standing water during vegetative stage.
Transplanting: 25-30 day old seedlings. Spacing 20cm x 15cm. 2-3 seedlings per hill.
Fertilizer: 100:50:50 kg NPK/ha. Split nitrogen: 50% basal, 25% at tillering, 25% at panicle initiation.
Common diseases: Blast (Pyricularia oryzae), Brown Spot, Sheath Blight, Bacterial Leaf Blight.
Blast control: Tricyclazole @ 0.6g/L or Carbendazim @ 1g/L. Avoid excess nitrogen.
Harvest: When 80-85% grains are golden yellow. Grain moisture should be 20-22%.
Yield: 5-7 tonnes/ha for improved varieties. Hybrid varieties can give 8-10 tonnes/ha.""",
        ),
        (
            "Wheat Cultivation Guide",
            "Crop Management",
            """Wheat (Triticum aestivum) is grown as rabi crop in India (October-March).
Temperature: 10-25°C. Best germination at 20-22°C. High temperature at grain fill reduces yield.
Soil: Well-drained loamy or clay-loam. pH 6.0-7.5.
Sowing: Line sowing at 20-22cm row spacing. Seed rate 100-125 kg/ha.
Irrigation: 5-6 irrigations critical at: Crown root initiation (21 days), Tillering (45 days), Jointing (65 days), Flowering (85 days), Grain filling (105 days).
Fertilizer: 120:60:40 kg NPK/ha. Full P and K as basal, N in splits.
Yellow rust (Stripe rust): Yellow stripes on leaves in cool humid weather. Apply Propiconazole @ 1ml/L.
Aphids: Attack at grain filling stage. Apply Dimethoate @ 1.5ml/L if population exceeds threshold.
Harvest: When grain moisture is 12-14%. Combine harvesting preferred.""",
        ),
    ]

    for title, category, content in docs:
        ingest_document(db, title, category, content)


@app.get("/")
def root():
    return {
        "name": "AgriPulse AI",
        "tagline": "Smart Advice. Better Farming.",
        "version": "1.0.0",
        "docs": "/docs",
    }
