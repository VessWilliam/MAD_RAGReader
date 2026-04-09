from pathlib import Path

from dotenv import load_dotenv
from langchain_core.utils import secret_from_env
from pydantic import SecretStr

load_dotenv()

GROQ_API_KEY: SecretStr = secret_from_env("GROQ_API_KEY")()
MAX_CHARS = 1500
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "pdf"
VECTORSTORE_PATH = BASE_DIR / "vectorstore"
PROMPT_TEMPLATE = """
You are a strict document QA assistant.

Rules:
- Only use the context below.
- If answer is not found, say:
  "I don't know based on the document."
- Keep answer short and factual.

Context:
{context}

Conversation:
{history}

Question:
{query}

Answer (be precise):
"""
