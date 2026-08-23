import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("groq_client")

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self._client = None

    def is_available(self) -> bool:
        """Returns True if GROQ_API_KEY is configured and client can be initialized."""
        return bool(self.api_key and self.api_key.strip())

    def _get_client(self):
        if self._client is None and self.is_available():
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self._client = None
        return self._client

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, timeout: float = 5.0) -> Optional[str]:
        """Generates text completion from Groq model."""
        client = self._get_client()
        if not client:
            return None

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=500,
                timeout=timeout
            )

            if completion and completion.choices:
                return completion.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq generate_text failed: {e}")

        return None

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, timeout: float = 5.0) -> Optional[str]:
        """Generates JSON object output from Groq model using response_format={'type': 'json_object'}."""
        client = self._get_client()
        if not client:
            return None

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=800,
                timeout=timeout
            )

            if completion and completion.choices:
                return completion.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq generate_structured failed: {e}")

        return None


# Global LLM Client instance
default_llm_client = LLMClient()


class MockLLMClient:
    """Mock LLM Client for offline unit and integration testing without live Groq credentials."""
    def __init__(self, predefined_json: Optional[str] = None, predefined_text: Optional[str] = None):
        self.predefined_json = predefined_json
        self.predefined_text = predefined_text
        self.is_active = True

    def is_available(self) -> bool:
        return self.is_active

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, timeout: float = 5.0) -> Optional[str]:
        if not self.is_active:
            return None
        if self.predefined_json is not None:
            return self.predefined_json
        return None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, timeout: float = 5.0) -> Optional[str]:
        if not self.is_active:
            return None
        if self.predefined_text is not None:
            return self.predefined_text
        return None
