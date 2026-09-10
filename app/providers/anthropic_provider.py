from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.providers.base import ModelProvider
from app.schemas import Message


class AnthropicProvider(ModelProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(self, messages: list[Message], stream: bool = True) -> AsyncIterator[str]:
        system = "\n".join(message.content for message in messages if message.role == "system")
        conversation = [message.model_dump() for message in messages if message.role != "system"]
        if stream:
            async with self.client.messages.stream(
                model=self.model, max_tokens=4096, system=system or None, messages=conversation
            ) as response:
                async for text in response.text_stream:
                    yield text
        else:
            response = await self.client.messages.create(
                model=self.model, max_tokens=4096, system=system or None, messages=conversation
            )
            for block in response.content:
                if block.type == "text":
                    yield block.text
