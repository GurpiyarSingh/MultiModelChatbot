import json
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.chat_service import ChatService
from app.config import settings
from app.schemas import ChatRequest, ChatResponse, ModelInfo, SessionDetail, SessionSummary
from app.session_store import SessionStore

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Multi-Model Chatbot", version="0.0.1")
store = SessionStore(settings.sessions_file)
service = ChatService(settings, store)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await service.chat(request)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        session_id: str | None = None
        try:
            async for session_id, token in service.stream(request):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
        except Exception as exc:
            logging.getLogger(__name__).exception("Streaming chat failed")
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.get("/sessions", response_model=list[SessionSummary])
async def list_sessions() -> list[SessionSummary]:
    return store.list()


@app.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str) -> SessionDetail:
    try:
        return store.detail(session_id)
    except KeyError:
        raise HTTPException(404, f"Session '{session_id}' was not found.") from None


@app.get("/models", response_model=list[ModelInfo])
async def list_models() -> list[ModelInfo]:
    return service.model_infos()
