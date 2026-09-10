from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base import ModelProvider
from app.schemas import Message


class OpenAIProvider(ModelProvider):
    """OpenAI chat completion provider backed by the async SDK."""

    def __init__(self, api_key: str, model: str) -> None:
        """Create the async OpenAI client and store the default model name."""
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, messages: list[Message], stream: bool = True) -> AsyncIterator[str]:
        """Yield the model's response text either as a stream or as a single final answer."""
        response = await self.client.chat.completions.create(
            model=self.model, messages=[message.model_dump() for message in messages], stream=stream
        )
        if stream:
            async for chunk in response:
                text = chunk.choices[0].delta.content
                if text:
                    yield text
        else:
            text = response.choices[0].message.content
            if text:
                yield text
