from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    farms = relationship("Farm", back_populates="user")


class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    location = Column(String(255))
    size_acres = Column(Float)
    soil_type = Column(String(100))
    irrigation_method = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="farms")
    crops = relationship("Crop", back_populates="farm")
    soil_records = relationship("SoilRecord", back_populates="farm")
    weather_records = relationship("WeatherRecord", back_populates="farm")
    ai_recommendations = relationship("AIRecommendation", back_populates="farm")
    timeline_events = relationship("FarmTimeline", back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    planted_date = Column(Date, nullable=True)
    age_days = Column(Integer, default=0)
    growth_stage = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    farm = relationship("Farm", back_populates="crops")


class SoilRecord(Base):
    __tablename__ = "soil_records"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    moisture_percent = Column(Float)
    ph_level = Column(Float)
    nitrogen_level = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    farm = relationship("Farm", back_populates="soil_records")


class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    temperature_celsius = Column(Float)
    humidity_percent = Column(Float)
    rain_probability_percent = Column(Float)
    wind_speed_kmh = Column(Float)
    rainfall_mm = Column(Float, nullable=True)
    is_demo = Column(Boolean, default=True)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    farm = relationship("Farm", back_populates="weather_records")


class CropHealth(Base):
    __tablename__ = "crop_health"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    image_filename = Column(String(255), nullable=True)
    analysis_result = Column(JSONB, nullable=True)
    disease_detected = Column(String(255), nullable=True)
    confidence_percent = Column(Float, nullable=True)
    is_demo_analysis = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    user_query = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    agents_used = Column(ARRAY(String), nullable=True)
    sources = Column(ARRAY(String), nullable=True)
    confidence = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    farm = relationship("Farm", back_populates="ai_recommendations")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    chunks = relationship("KnowledgeChunk", back_populates="document")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"))
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    document = relationship("KnowledgeDocument", back_populates="chunks")


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, nullable=True)
    query = Column(Text)
    agent_name = Column(String(100))
    result = Column(JSONB, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class FarmTimeline(Base):
    __tablename__ = "farm_timeline"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    event_type = Column(String(100), nullable=False)
    event_description = Column(Text, nullable=False)
    event_icon = Column(String(10), nullable=True)
    event_date = Column(Date, nullable=False)
    day_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    farm = relationship("Farm", back_populates="timeline_events")
