import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "chat.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class SQLiteDatabase:
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH))
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

    def save_message(self, session_id: str, question: str, answer: str) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                    INSERT INTO chat_history (session_id, question, answer)
                    VALUES (?, ?, ?)
                    """,
                (session_id, question, answer),
            )
            conn.commit()

    def get_history(self, session_id: str, limit: int = 3) -> list[dict]:
        with self.get_connection() as conn:
            row = conn.execute(
                """
                  Select question, answer from chat_history
                  WHERE session_id = ?
                  ORDER BY created_at DESC
                  LIMIT ?
                 """,
                (session_id, limit),
            ).fetchall()

            return [{"question": r[0], "answer": r[1]} for r in reversed(row)]

    def clear_history(self, session_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                DELETE FROM chat_history
                WHERE session_id = ?
                """,
                (session_id,),
            )
            conn.commit()
