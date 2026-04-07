from ..repo import SQLiteDatabase

db = SQLiteDatabase()


class ClearService:
    def clear_history(self, session_id: str) -> None:
        db.clear_history(session_id)
