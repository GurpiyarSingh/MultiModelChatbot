from collections.abc import AsyncIterator

from fastapi import HTTPException

from app.config import Settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import ModelProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.local_provider import LocalProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas import ChatRequest, ChatResponse, Message, ModelInfo
from app.session_store import SessionStore


class ChatService:
    def __init__(self, settings: Settings, store: SessionStore) -> None:
        self.settings = settings
        self.store = store

    def model_infos(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="claude-sonnet", provider="anthropic", available=bool(self.settings.anthropic_api_key)),
            ModelInfo(id="gpt-4o-mini", provider="openai", available=bool(self.settings.openai_api_key)),
            ModelInfo(id=self.settings.gemini_model, provider="gemini", available=bool(self.settings.gemini_api_key)),
            ModelInfo(id=self.settings.groq_model, provider="groq", available=bool(self.settings.groq_api_key)),
            ModelInfo(id=self.settings.ollama_model, provider="ollama", available=True),
        ]

    def _provider(self, model: str) -> ModelProvider:
        normalized = model.lower()
        if normalized.startswith(("claude", "anthropic/")):
            if not self.settings.anthropic_api_key:
                raise HTTPException(400, "ANTHROPIC_API_KEY is required for Anthropic models.")
            return AnthropicProvider(self.settings.anthropic_api_key, model.removeprefix("anthropic/"))
        if normalized.startswith(("gpt", "o1", "o3", "openai/")):
            if not self.settings.openai_api_key:
                raise HTTPException(400, "OPENAI_API_KEY is required for OpenAI models.")
            return OpenAIProvider(self.settings.openai_api_key, model.removeprefix("openai/"))
        if normalized in {"gemini", self.settings.gemini_model.lower()}:
            if not self.settings.gemini_api_key:
                raise HTTPException(400, "GEMINI_API_KEY is required for Gemini models.")
            return GeminiProvider(self.settings.gemini_api_key, self.settings.gemini_api_url, self.settings.gemini_model)
        if normalized in {"groq", self.settings.groq_model.lower()}:
            if not self.settings.groq_api_key:
                raise HTTPException(400, "GROQ_API_KEY is required for Groq models.")
            return GroqProvider(self.settings.groq_api_key, self.settings.groq_api_url, self.settings.groq_model)
        if normalized in {"local", "ollama", self.settings.ollama_model.lower()}:
            return LocalProvider(self.settings.ollama_url, self.settings.ollama_model if normalized in {"local", "ollama"} else model)
        raise HTTPException(400, f"Unknown model '{model}'. Use /models to see configured choices.")

    def start(self, request: ChatRequest) -> tuple[str, str, ModelProvider, list[Message]]:
        model = request.model or self.settings.default_model
        provider = self._provider(model)
        try:
            session_id = self.store.create_or_get(request.session_id, model)
        except KeyError:
            raise HTTPException(404, f"Session '{request.session_id}' was not found.") from None
        self.store.add_message(session_id, Message(role="user", content=request.message))
        return session_id, model, provider, self.store.messages(session_id)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        session_id, model, provider, messages = self.start(request)
        reply = "".join([chunk async for chunk in provider.generate(messages, stream=False)])
        self.store.add_message(session_id, Message(role="assistant", content=reply))
        return ChatResponse(session_id=session_id, model=model, message=Message(role="assistant", content=reply))

    async def stream(self, request: ChatRequest) -> AsyncIterator[tuple[str, str]]:
        session_id, model, provider, messages = self.start(request)
        reply = ""
        async for chunk in provider.generate(messages, stream=True):
            reply += chunk
            yield session_id, chunk
        self.store.add_message(session_id, Message(role="assistant", content=reply))
