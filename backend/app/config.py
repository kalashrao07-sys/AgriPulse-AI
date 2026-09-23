from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://agrisaarthi:agrisaarthi123@localhost:5432/agrisaarthi"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    AI_PROVIDER: str = "ollama"  # "ollama" or "ibm"

    # IBM watsonx.ai settings (optional)
    IBM_WATSONX_API_KEY: Optional[str] = None
    IBM_WATSONX_PROJECT_ID: Optional[str] = None
    IBM_WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    IBM_GRANITE_MODEL: str = "ibm/granite-13b-instruct-v2"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
