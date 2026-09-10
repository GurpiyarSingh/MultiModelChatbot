from langchain_groq import ChatGroq

from app.providers.langchain_adapter import LangChainChatProvider


class GroqProvider(LangChainChatProvider):
    """Groq through LangChain's Groq integration."""

    def __init__(self, api_key: str, api_url: str, model: str) -> None:
        base_url = api_url.removesuffix("/chat/completions")
        super().__init__(ChatGroq(model=model, groq_api_key=api_key, base_url=base_url))
