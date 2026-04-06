import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repo import SQLiteDatabase

db = SQLiteDatabase()


client = TestClient(app)
HI = "Hi"
SESSION_ID = "test-session-123"
HEADERS = {"session-id": SESSION_ID}
QUESTION = "what is rag?"
ANSWER = "RAG stands for Retrieval-Augmented Generation."
HELLO = "Hello World"
LIMIT_SESSION = "limit-session"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": HELLO}


def test_ask_short_query():
    response = client.post("/ask", json={"query": HI}, headers=HEADERS)
    assert response.status_code == 200
    content = b"".join(response.iter_bytes()).decode()
    assert "Please ask a more specific question" in content


def test_ask_missing_session_id():
    response = client.post("/ask", json={"query": QUESTION})
    assert response.status_code == 422


def test_ask_valid_query():
    response = client.post("/ask", json={"query": QUESTION}, headers=HEADERS)
    assert response.status_code == 200
    content = b"".join(response.iter_bytes()).decode()
    assert len(content) > 0


def test_clear_history():
    response = client.post("/clear", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"message": "Conversation history cleared."}


def test_sqlite_save_and_retrieve():
    db.init_db()

    db.save_message(SESSION_ID, QUESTION, ANSWER)
    history = db.get_history("test-session-123")

    assert len(history) >= 1
    assert history[-1]["question"] == QUESTION
    assert history[-1]["answer"] == ANSWER

    db.clear_history(SESSION_ID)
    history = db.get_history(SESSION_ID)
    assert len(history) == 0


def test_sqlite_history_limit():
    db.clear_history(LIMIT_SESSION)
    for i in range(15):
        db.save_message(LIMIT_SESSION, f"Question {i}", f"Answer {i}")
    history = db.get_history(LIMIT_SESSION, limit=3)
    assert len(history) == 3
    db.clear_history(LIMIT_SESSION)
