export interface FarmData {
  farm_id: number;
  user_id: number;
  farmer_name: string;
  location: string;
  size_acres: number;
  soil_type: string;
  irrigation_method: string;
  crop_name: string;
  crop_age_days: number;
  growth_stage: string;
  soil_moisture: number;
  soil_ph: number;
  temperature: number;
  humidity: number;
  rain_probability: number;
  wind_speed: number;
  is_demo_weather: boolean;
}

export interface AdvisoryResponse {
  query: string;
  recommendation: string;
  agents_used: string[];
  sources: string[];
  confidence: string;
  provider: string;
}

export interface CropHealthResult {
  agent: string;
  is_demo: boolean;
  demo_notice: string;
  crop: string;
  image_filename: string | null;
  disease_detected: string;
  confidence_percent: number;
  severity: string;
  symptoms: string;
  treatment: string;
  prevention: string;
  ai_text_response?: string;
}

export interface WeatherData {
  temperature_celsius: number;
  humidity_percent: number;
  rain_probability_percent: number;
  wind_speed_kmh: number;
  description: string;
  is_demo: boolean;
  soil_moisture_percent: number;
  irrigation_recommendation: {
    decision: string;
    color: string;
    reason: string;
    icon: string;
  };
  demo_notice: string | null;
}

export interface TimelineEvent {
  id: number;
  event_type: string;
  description: string;
  icon: string;
  date: string;
  day_number: number | null;
  is_today: boolean;
}

export interface HealthStatus {
  status: string;
  database: string;
  ai_provider: string;
  ai_available: boolean;
  rag_chunks: number;
  rag_ready: boolean;
  agents: Record<string, string>;
  config: {
    ai_provider: string;
    ollama_model: string;
  };
}
