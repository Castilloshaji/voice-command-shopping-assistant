from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.intent import VoiceParseRequest, ParsedIntent, IntentEnum
from app.schemas.command import CommandExecutionResponse
from app.services.nlp_service import NLPService
from app.services.command_service import CommandService

router = APIRouter(
    prefix="/voice",
    tags=["voice"]
)

@router.post("/parse", response_model=ParsedIntent, status_code=status.HTTP_200_OK)
def parse_voice_command(request: VoiceParseRequest) -> ParsedIntent:
    """
    Parses a natural language text command into a structured intent.
    This endpoint is strictly non-mutating and performs text parsing only.
    """
    return NLPService.parse_transcript(request.text, request.language or "en-US")

@router.post("/execute", response_model=CommandExecutionResponse, status_code=status.HTTP_200_OK)
def execute_voice_command(
    request: VoiceParseRequest,
    db: Session = Depends(get_db)
) -> CommandExecutionResponse:
    """
    Parses natural language text and executes the corresponding command orchestration.
    """
    parsed = NLPService.parse_transcript(request.text, request.language or "en-US")

    if parsed.intent == IntentEnum.UNKNOWN:
        return CommandExecutionResponse(
            success=False,
            intent=IntentEnum.UNKNOWN,
            message="I couldn't understand that command.",
            data=None
        )

    return CommandService.execute_command(db, parsed)
