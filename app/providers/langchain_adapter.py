from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.providers.base import ModelProvider
from app.schemas import Message


def to_langchain_messages(messages: list[Message]) -> list[BaseMessage]:
    """Translate API messages once, so every LangChain chat model receives the same history."""
    mapping = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}
    return [mapping[message.role](content=message.content) for message in messages]


def content_as_text(content: Any) -> str:
    """Normalize LangChain content payloads into a plain string for downstream processing."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content or "")


class LangChainChatProvider(ModelProvider):
    """Adapter from LangChain's Runnable chat-model API to the portable provider contract."""

    def __init__(self, model: Any) -> None:
        """Wrap a LangChain chat model behind the common provider interface."""
        self.model = model

    async def generate(self, messages: list[Message], stream: bool = True) -> AsyncIterator[str]:
        """Generate text from the wrapped LangChain model, either as a stream or one final reply."""
        history = to_langchain_messages(messages)
        if stream:
            async for chunk in self.model.astream(history):
                text = content_as_text(chunk.content)
                if text:
                    yield text
        else:
            response = await self.model.ainvoke(history)
            text = content_as_text(response.content)
            if text:
                yield text
