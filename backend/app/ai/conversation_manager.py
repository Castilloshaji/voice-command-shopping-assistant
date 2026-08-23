from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class TurnContext(BaseModel):
    user_text: str
    intent: str
    items: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    success: bool = True
    clarification_question: Optional[str] = None


class ConversationSession(BaseModel):
    session_id: str
    turns: List[TurnContext] = Field(default_factory=list)
    pending_clarification: Optional[Dict[str, Any]] = None
    pending_checkout: Optional[Dict[str, Any]] = None

    def add_turn(self, turn: TurnContext):
        self.turns.append(turn)
        if len(self.turns) > 5:
            self.turns = self.turns[-5:]

    def get_last_turn(self) -> Optional[TurnContext]:
        if self.turns:
            return self.turns[-1]
        return None

    def format_context_prompt(self) -> str:
        """Formats recent session turns as context string for LLM prompt."""
        if not self.turns and not self.pending_clarification:
            return ""

        lines = ["Recent Conversation Context:"]
        for idx, turn in enumerate(self.turns[-3:], 1):
            lines.append(f"Turn {idx}: User said '{turn.user_text}' -> Intent: {turn.intent}")
            if turn.items:
                items_str = ", ".join(f"{i.get('item')} (qty={i.get('quantity')}, unit={i.get('unit')})" for i in turn.items)
                lines.append(f"  Resulting Items: {items_str}")
            if turn.suggestions:
                sugg_str = ", ".join(s.get("name", "") for s in turn.suggestions)
                lines.append(f"  Offered Candidates: {sugg_str}")

        if self.pending_clarification:
            lines.append(f"Pending Clarification: {self.pending_clarification}")

        return "\n".join(lines)


class ConversationManager:
    """In-memory store for session conversation context."""
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def get_or_create_session(self, session_id: Optional[str]) -> Optional[ConversationSession]:
        if not session_id:
            return None
        sid = session_id.strip()
        if not sid:
            return None
        if sid not in self._sessions:
            self._sessions[sid] = ConversationSession(session_id=sid)
        return self._sessions[sid]

    def record_turn(
        self,
        session_id: Optional[str],
        user_text: str,
        intent: str,
        items: Optional[List[Dict[str, Any]]] = None,
        suggestions: Optional[List[Dict[str, Any]]] = None,
        success: bool = True,
        clarification_question: Optional[str] = None
    ):
        session = self.get_or_create_session(session_id)
        if not session:
            return

        turn = TurnContext(
            user_text=user_text,
            intent=intent,
            items=items or [],
            suggestions=suggestions or [],
            success=success,
            clarification_question=clarification_question
        )
        session.add_turn(turn)

        if clarification_question or (suggestions and not success):
            session.pending_clarification = {
                "question": clarification_question,
                "candidates": suggestions or []
            }
        else:
            session.pending_clarification = None

    def clear_session(self, session_id: Optional[str]):
        if session_id and session_id in self._sessions:
            del self._sessions[session_id]


# Global Conversation Manager instance
conversation_manager = ConversationManager()
