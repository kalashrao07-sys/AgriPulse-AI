"""
AI Provider Abstraction Layer
Supports: Ollama (local) and IBM watsonx.ai (production)
Switch via AI_PROVIDER env var: "ollama" or "ibm"
"""
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from app.config import settings


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the AI model."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass


class OllamaProvider(AIProvider):
    """Local Ollama provider using open-source Llama models."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    @property
    def provider_name(self) -> str:
        return f"Ollama ({self.model})"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 800,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


class IBMWatsonxProvider(AIProvider):
    """IBM watsonx.ai provider using Granite models."""

    def __init__(self):
        self.api_key = settings.IBM_WATSONX_API_KEY
        self.project_id = settings.IBM_WATSONX_PROJECT_ID
        self.url = settings.IBM_WATSONX_URL
        self.model = settings.IBM_GRANITE_MODEL
        self._iam_token: Optional[str] = None

    @property
    def provider_name(self) -> str:
        return f"IBM watsonx.ai ({self.model})"

    async def _get_iam_token(self) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.api_key,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key or not self.project_id:
            raise ValueError("IBM watsonx.ai credentials not configured. Set IBM_WATSONX_API_KEY and IBM_WATSONX_PROJECT_ID.")

        token = await self._get_iam_token()
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.url}/ml/v1/text/generation?version=2023-05-29",
                json={
                    "model_id": self.model,
                    "input": full_prompt,
                    "parameters": {
                        "decoding_method": "greedy",
                        "max_new_tokens": 800,
                        "temperature": 0.3,
                    },
                    "project_id": self.project_id,
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["generated_text"].strip()

    async def is_available(self) -> bool:
        return bool(self.api_key and self.project_id)


def get_ai_provider() -> AIProvider:
    """Factory: returns the configured AI provider."""
    provider = settings.AI_PROVIDER.lower()
    if provider == "ibm":
        return IBMWatsonxProvider()
    return OllamaProvider()
