from fastapi import APIRouter, status
from app.schemas.intent import VoiceParseRequest, ParsedIntent
from app.services.nlp_service import NLPService

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
