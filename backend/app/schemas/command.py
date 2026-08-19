from typing import Optional, Any
from pydantic import BaseModel
from app.schemas.intent import IntentEnum

class CommandExecutionResponse(BaseModel):
    success: bool
    intent: IntentEnum
    message: str
    data: Optional[Any] = None
