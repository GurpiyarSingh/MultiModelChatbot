from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base import ModelProvider
from app.schemas import Message


class OpenAIProvider(ModelProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, messages: list[Message], stream: bool = True) -> AsyncIterator[str]:
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
