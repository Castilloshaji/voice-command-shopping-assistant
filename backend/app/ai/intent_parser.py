import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.intent import ParsedIntent, IntentEnum, IntentItem
from app.ai.llm_client import LLMClient, default_llm_client
from app.ai.prompts import INTENT_PARSER_SYSTEM_PROMPT
from app.ai.conversation_manager import conversation_manager

logger = logging.getLogger("ai_intent_parser")


class LLMIntentItem(BaseModel):
    item: str
    quantity: float = 1.0
    unit: Optional[str] = None


class LLMIntent(BaseModel):
    intent: IntentEnum
    items: List[LLMIntentItem] = Field(default_factory=list)
    query: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    target_item: Optional[str] = None
    target_quantity: Optional[float] = None
    confidence: float = 1.0
    clarification_required: bool = False
    clarification_question: Optional[str] = None


class AIIntentParser:
    @staticmethod
    def parse_intent(
        transcript: str,
        language: str = "en-US",
        session_id: Optional[str] = None,
        llm_client: Optional[LLMClient] = None
    ) -> Optional[ParsedIntent]:
        """
        Parses transcript into a structured ParsedIntent using Groq LLM.
        Returns None if LLM is unavailable, times out, or produces invalid output,
        signaling automatic fallback to deterministic NLPService.
        """
        client = llm_client or default_llm_client
        if not client.is_available():
            logger.info("Groq LLM client is unavailable or unconfigured. Skipping AI intent parsing.")
            return None

        # Build prompt with conversation context if session_id is provided
        session = conversation_manager.get_or_create_session(session_id)
        context_str = session.format_context_prompt() if session else ""

        full_prompt = f"User Transcript: '{transcript}'"
        if context_str:
            full_prompt = f"{context_str}\n\nCurrent User Input: '{transcript}'"

        json_response = client.generate_structured(
            prompt=full_prompt,
            system_prompt=INTENT_PARSER_SYSTEM_PROMPT,
            timeout=4.0
        )

        if not json_response:
            logger.warning("LLM generate_structured returned empty/None output.")
            return None

        try:
            data = json.loads(json_response)
            llm_intent = LLMIntent.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to validate LLM JSON response against LLMIntent schema: {e}")
            return None

        # Convert valid LLMIntent to standard ParsedIntent
        intent_items = [
            IntentItem(item=i.item, quantity=i.quantity, unit=i.unit)
            for i in llm_intent.items
        ]

        first_item = intent_items[0].item if intent_items else (llm_intent.target_item or llm_intent.query)
        first_qty = intent_items[0].quantity if intent_items else (llm_intent.target_quantity or 1.0)
        first_unit = intent_items[0].unit if intent_items else None

        return ParsedIntent(
            intent=llm_intent.intent,
            item=first_item,
            quantity=first_qty if llm_intent.intent in (IntentEnum.ADD_ITEM, IntentEnum.UPDATE_QUANTITY, IntentEnum.REMOVE_ITEM) else None,
            unit=first_unit,
            items=intent_items if intent_items else None,
            max_price=llm_intent.max_price,
            min_price=llm_intent.min_price,
            brand=llm_intent.brand,
            category=llm_intent.category,
            confidence=llm_intent.confidence,
            original_text=transcript,
            normalized_text=transcript.strip().lower(),
            message=llm_intent.clarification_question if llm_intent.clarification_required else None
        )
