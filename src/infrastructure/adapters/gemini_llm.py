import logging
from google import genai
from src.domain.ports.llm import LLMPort
from src.infrastructure.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)


class GeminiLLMAdapter(LLMPort):
    """Generates completions using Gemini Flash via Google GenAI SDK."""

    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self._client = None
        if api_key:
            self._client = genai.Client(api_key=api_key)

    def generate_answer(self, prompt: str) -> str:
        if not self._client:
            return (
                "[MODO DEMO / SIN CREDENCIALES LLM]\n"
                "El sistema recuperó los fragmentos pertinentes y aplicó los guardrails con éxito.\n"
                "Para generar la respuesta con Gemini, configura GEMINI_API_KEY en tu archivo .env."
            )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text or ""
