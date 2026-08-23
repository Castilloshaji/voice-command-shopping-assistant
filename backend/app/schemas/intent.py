from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class IntentEnum(str, Enum):
    ADD_ITEM = "ADD_ITEM"
    REMOVE_ITEM = "REMOVE_ITEM"
    UPDATE_QUANTITY = "UPDATE_QUANTITY"
    SEARCH_PRODUCT = "SEARCH_PRODUCT"
    SHOW_LIST = "SHOW_LIST"
    CLEAR_LIST = "CLEAR_LIST"
    GET_SUGGESTIONS = "GET_SUGGESTIONS"
    UNKNOWN = "UNKNOWN"

class VoiceParseRequest(BaseModel):
    text: str = Field(..., description="Canonical natural language command text")
    language: Optional[str] = Field(default="en-US", description="Language code")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier for conversation context")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text cannot be empty or whitespace")
        return v

class IntentItem(BaseModel):
    item: str
    quantity: float = 1.0
    unit: Optional[str] = None

class ParsedIntent(BaseModel):
    intent: IntentEnum
    item: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    items: Optional[List[IntentItem]] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 1.0
    original_text: str
    normalized_text: Optional[str] = None
    message: Optional[str] = None
