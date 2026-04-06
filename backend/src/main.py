from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from fastapi.params import Depends
import uvicorn
from fastapi import FastAPI, Header
from .services import MainService
from .repo import SQLiteDatabase
from pydantic import BaseModel
import asyncio

db = SQLiteDatabase()
service = MainService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(lifespan=lifespan)


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(req: QueryRequest, session_id: str = Header(...)):
    async def event_stream():
        try:
            async for token in service.ask_stream(session_id, req.query):
                yield f"data: {token}\n\n"
                await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
        except Exception as e:
            print("PRINT ERROR:", e)
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/clear")
def clear(session_id: str = Header(...)):
    service.clear_history(session_id)
    return {"message": "Conversation history cleared."}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
