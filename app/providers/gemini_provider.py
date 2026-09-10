from langchain_google_genai import ChatGoogleGenerativeAI

from app.providers.langchain_adapter import LangChainChatProvider


class GeminiProvider(LangChainChatProvider):
    """Gemini through LangChain's Google integration."""

    def __init__(self, api_key: str, api_url: str, model: str) -> None:
        """Create the Gemini LangChain client and retain the configured API base URL."""
        # The configured v1beta URL is Google's standard endpoint used by this integration.
        # Keep it in configuration for API-contract parity and future endpoint customization.
        self.api_url = api_url
        super().__init__(ChatGoogleGenerativeAI(model=model, google_api_key=api_key))
