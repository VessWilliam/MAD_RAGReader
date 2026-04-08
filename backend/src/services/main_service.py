import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..repo import SQLiteDatabase

load_dotenv()
db = SQLiteDatabase()
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


class MainService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is not set in the environment variables."
            )

        embedding = FastEmbedEmbeddings()
        self.vectorstore = self._load_or_build_vectorstore(embedding)
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="qwen/qwen3-32b",
            temperature=0.5,
            max_tokens=400,
            reasoning_effort="none",
        )

    async def ask_stream(self, session_id: str, query: str):
        try:
            if len(query.strip()) < 5:
                yield "Please ask a more specific question related to the document."
                return

            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=4)
            docs_with_scores = sorted(docs_with_scores, key=lambda x: x[1])

            filtered_docs = [doc for doc, score in docs_with_scores[:3] if score < 1.0]

            if not filtered_docs:
                yield "I don't know based on the document."
                return

            context = ""
            for doc in filtered_docs:
                if len(context) + len(doc.page_content) > MAX_CHARS:
                    break
                context += doc.page_content[:500] + "\n\n"

            prompt = self._build_prompt(query, context, session_id)

            full_answer = ""

            async for chunk in self.llm.astream(prompt):
                content = getattr(chunk, "content", None)

                if not content:
                    continue

                full_answer += content
                yield content

            try:
                db.save_message(session_id, query, full_answer)
            except Exception as e:
                print("DB ERROR:", e)
        except Exception as e:
            print("LLM ERROR:", e)
            yield f"[ERROR] {str(e)}"

    ## Private Helper Methods

    def _format_history(self, session_id: str) -> str:
        history = db.get_history(session_id)
        if not history:
            return "No Previous Conversation History."

        return "\n".join(
            f"User: {entry['question']}\nAI: {entry['answer']}" for entry in history
        )

    def _build_prompt(self, query: str, context: str, session_id: str) -> str:
        return PROMPT_TEMPLATE.format(
            context=context, history=self._format_history(session_id), query=query
        )

    def _load_or_build_vectorstore(self, embedding: FastEmbedEmbeddings) -> FAISS:
        index_file = VECTORSTORE_PATH / "index.faiss"
        if index_file.exists():
            return FAISS.load_local(
                str(VECTORSTORE_PATH),
                embeddings=embedding,
                allow_dangerous_deserialization=True,
            )
        return self._build_vectorstore(embedding)

    def _build_vectorstore(self, embedding: FastEmbedEmbeddings) -> FAISS:
        self._validate_data_directory()

        chunks = self._load_and_split_documents()
        vectorstore = FAISS.from_documents(chunks, embedding)
        vectorstore.save_local(str(VECTORSTORE_PATH))

        return vectorstore

    def _validate_data_directory(self) -> None:
        if not DATA_DIR.exists():
            raise FileNotFoundError(f"Data directory not found at {DATA_DIR}")

        if not any(DATA_DIR.glob("**/*.pdf")):
            raise FileNotFoundError(
                f"No PDF files found in data directory at {DATA_DIR}"
            )

    def _load_and_split_documents(self) -> list:
        loader = DirectoryLoader(str(DATA_DIR), glob="**/*.pdf", loader_cls=PyPDFLoader)
        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        return splitter.split_documents(loader.load())
