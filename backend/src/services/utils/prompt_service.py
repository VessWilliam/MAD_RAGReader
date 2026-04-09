from ...database import SQLiteDatabase
from ..config import PROMPT_TEMPLATE


class PromptService:
    def __init__(self, db: SQLiteDatabase):
        self.db = db

    def build_prompt(self, query: str, context: str, session_id: str) -> str:
        return PROMPT_TEMPLATE.format(
            context=context,
            history=self._format_history(session_id),
            query=query,
        )

    def _format_history(self, session_id: str) -> str:
        history = self.db.get_history(session_id)
        if not history:
            return "No Previous Conversation History."
        return "\n".join(
            f"User: {entry['question']}\nAI: {entry['answer']}" for entry in history
        )
