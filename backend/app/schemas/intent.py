from enum import Enum
from typing import Optional
from pydantic import BaseModel

class IntentEnum(str, Enum):
    ADD_ITEM = "ADD_ITEM"
    REMOVE_ITEM = "REMOVE_ITEM"
    UPDATE_QUANTITY = "UPDATE_QUANTITY"
    SEARCH_PRODUCT = "SEARCH_PRODUCT"
    SHOW_LIST = "SHOW_LIST"
    CLEAR_LIST = "CLEAR_LIST"
    GET_SUGGESTIONS = "GET_SUGGESTIONS"

class VoiceParseRequest(BaseModel):
    transcript: str
    language: Optional[str] = "en-US"

class ParsedIntent(BaseModel):
    intent: IntentEnum
    item: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    raw_transcript: str
    confidence: Optional[float] = 1.0
