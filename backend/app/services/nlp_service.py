from app.schemas.intent import ParsedIntent, IntentEnum

class NLPService:
    """
    Interface & engine contract for converting natural language voice transcripts
    into structured intents for shopping list operations.
    Full parser implementation will be added in Phase 3.
    """
    @staticmethod
    def parse_transcript(transcript: str, language: str = "en-US") -> ParsedIntent:
        # Interface placeholder signature
        return ParsedIntent(
            intent=IntentEnum.ADD_ITEM,
            item=None,
            quantity=None,
            unit=None,
            category=None,
            raw_transcript=transcript
        )
