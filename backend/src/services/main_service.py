from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_groq import ChatGroq

from ..database import SQLiteDatabase
from .config import GROQ_API_KEY, MAX_CHARS
from .utils import PromptService, VectorStoreService


class MainService:
    def __init__(self):
        if not GROQ_API_KEY:
            raise EnvironmentError(
                "GROQ_API_KEY is not set in the environment variables."
            )

        db = SQLiteDatabase()
        embedding = FastEmbedEmbeddings()

        self.db = db
        self.vectorstore = VectorStoreService().load_or_build(embeddings=embedding)
        self.prompt_service = PromptService(db)
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="qwen/qwen3-32b",
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

            prompt = self.prompt_service.build_prompt(query, context, session_id)

            full_answer = ""

            async for chunk in self.llm.astream(prompt):
                content = getattr(chunk, "content", None)

                if not content:
                    continue

                full_answer += content
                yield content

            try:
                self.db.save_message(session_id, query, full_answer)
            except Exception as e:
                print("DB ERROR:", e)
        except Exception as e:
            print("LLM ERROR:", e)
            yield f"[ERROR] {str(e)}"
