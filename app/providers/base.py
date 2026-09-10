from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.schemas import Message


class ModelProvider(ABC):
    """Portable provider contract shared with the production backend."""

    @abstractmethod
    async def generate(self, messages: list[Message], stream: bool = True) -> AsyncIterator[str]:
        """Yield generated text chunks for a conversation."""
        raise NotImplementedError
