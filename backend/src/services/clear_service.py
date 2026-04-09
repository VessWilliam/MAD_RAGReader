from ..database import SQLiteDatabase


class ClearService:
    def __init__(self):
        self.db = SQLiteDatabase()

    def clear_history(self, session_id: str) -> None:
        self.db.clear_history(session_id)
