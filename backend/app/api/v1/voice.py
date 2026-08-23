from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.intent import VoiceParseRequest, ParsedIntent, IntentEnum
from app.schemas.command import CommandExecutionResponse
from app.services.nlp_service import NLPService
from app.services.command_service import CommandService
from app.ai.intent_parser import AIIntentParser
from app.ai.response_generator import AIResponseGenerator
from app.ai.conversation_manager import conversation_manager

router = APIRouter(
    prefix="/voice",
    tags=["voice"]
)

def _parse_hybrid(request: VoiceParseRequest) -> ParsedIntent:
    """
    Hybrid intent parsing strategy:
    1. If AI parser is enabled and available, attempt AI parsing with conversation context.
    2. On failure, missing key, or low confidence, fall back automatically to deterministic NLPService.
    """
    if settings.ENABLE_AI_PARSER:
        ai_parsed = AIIntentParser.parse_intent(
            transcript=request.text,
            language=request.language or "en-US",
            session_id=request.session_id
        )
        if ai_parsed and ai_parsed.intent != IntentEnum.UNKNOWN:
            return ai_parsed

    # Fallback to deterministic NLPService
    return NLPService.parse_transcript(request.text, request.language or "en-US")


@router.post("/parse", response_model=ParsedIntent, status_code=status.HTTP_200_OK)
def parse_voice_command(request: VoiceParseRequest) -> ParsedIntent:
    """
    Parses a natural language text command into a structured intent.
    This endpoint is strictly non-mutating and performs text parsing only.
    """
    return _parse_hybrid(request)


@router.post("/execute", response_model=CommandExecutionResponse, status_code=status.HTTP_200_OK)
def execute_voice_command(
    request: VoiceParseRequest,
    db: Session = Depends(get_db)
) -> CommandExecutionResponse:
    """
    Parses natural language text and executes the corresponding command orchestration.
    """
    parsed = _parse_hybrid(request)

    if parsed.intent == IntentEnum.UNKNOWN:
        res = CommandExecutionResponse(
            success=False,
            intent=IntentEnum.UNKNOWN,
            message=parsed.message or "I couldn't understand that command.",
            data=None
        )
        conversation_manager.record_turn(
            session_id=request.session_id,
            user_text=request.text,
            intent=IntentEnum.UNKNOWN,
            success=False,
            clarification_question=res.message
        )
        return res

    execution_res = CommandService.execute_command(db, parsed)

    # Optionally polish natural assistant response via LLM if enabled
    if settings.ENABLE_AI_RESPONSES and execution_res.message:
        natural_msg = AIResponseGenerator.generate_natural_response(parsed, execution_res)
        execution_res.message = natural_msg

    # Record turn in ConversationManager
    items_list = []
    if parsed.items:
        items_list = [{"item": i.item, "quantity": i.quantity, "unit": i.unit} for i in parsed.items]
    elif parsed.item:
        items_list = [{"item": parsed.item, "quantity": parsed.quantity or 1.0, "unit": parsed.unit}]

    sugg_list = []
    if execution_res.data and isinstance(execution_res.data, dict) and "suggestions" in execution_res.data:
        sugg_list = execution_res.data["suggestions"]

    conversation_manager.record_turn(
        session_id=request.session_id,
        user_text=request.text,
        intent=parsed.intent,
        items=items_list,
        suggestions=sugg_list,
        success=execution_res.success,
        clarification_question=execution_res.message if not execution_res.success else None
    )

    return execution_res
