import logging
from typing import Optional
from app.schemas.intent import ParsedIntent
from app.schemas.command import CommandExecutionResponse
from app.ai.llm_client import LLMClient, default_llm_client
from app.ai.prompts import RESPONSE_GENERATOR_SYSTEM_PROMPT

logger = logging.getLogger("ai_response_generator")

class AIResponseGenerator:
    @staticmethod
    def generate_natural_response(
        parsed_intent: ParsedIntent,
        execution_response: CommandExecutionResponse,
        llm_client: Optional[LLMClient] = None
    ) -> str:
        """
        Generates a natural conversational user response using Groq LLM AFTER backend execution has completed.
        Falls back to execution_response.message if LLM is unavailable or unconfigured.
        """
        fallback_msg = execution_response.message or "Command executed successfully."

        client = llm_client or default_llm_client
        if not client.is_available():
            return fallback_msg

        prompt = (
            f"User Command: '{parsed_intent.original_text}'\n"
            f"Intent: {parsed_intent.intent}\n"
            f"Success Status: {execution_response.success}\n"
            f"Backend Result Message: '{execution_response.message}'\n"
        )

        natural_res = client.generate_text(
            prompt=prompt,
            system_prompt=RESPONSE_GENERATOR_SYSTEM_PROMPT,
            timeout=3.0
        )

        if natural_res and natural_res.strip():
            return natural_res.strip()

        return fallback_msg
