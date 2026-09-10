from langchain_ollama import ChatOllama

from app.providers.langchain_adapter import LangChainChatProvider


class LocalProvider(LangChainChatProvider):
    """Ollama via LangChain's maintained Ollama integration."""

    def __init__(self, url: str, model: str) -> None:
        super().__init__(ChatOllama(model=model, base_url=url.rstrip("/")))
